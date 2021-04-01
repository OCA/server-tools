# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import uuid
import psycopg2
import io
import ast

from datetime import datetime

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import ValidationError

try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib


def _get_external_id(record):
    # code reference from from odoo BaseModel.__ensure_xml_id() for generating the external_id
    """Create missing external ids for records, and return an
        dict of pairs ``(record, xmlid)`` for the records.

    :rtype: {'record': [Model, str | None]}
    """
    record and record.ensure_one()

    res = record._get_external_ids()
    if res[record.id]:
        return res

    modname = "__sync_process__"
    # create missing xml id
    rec_name = "%s_%s_%s" % (
        record._table,
        record.id,
        uuid.uuid4().hex[:8],
    )
    vals = {
        "module": modname,
        "model": record._name,
        "name": rec_name,
        "res_id": record.id,
    }
    record.env["ir.model.data"].create(vals)
    return record._get_external_ids()


class AuditlogLog(models.Model):
    _inherit = "auditlog.log"

    state = fields.Selection(
        [
            ("logged", "Logged"),
            ("captured", "Captured"),
            ("Prepared", "Prepared"),
            ("Pushed", "Pushed"),
            ("Pulled", "Pulled"),
            ("Processed", "Processed"),
            ("Error", "Error"),
            ("Failed", "Failed"),
            ("Cancelled", "Cancelled"),
        ],
        string="State",
        default="logged",
    )
    log_type = fields.Selection(selection_add=[("no_log", "No Log (Sync)")])
    model_name = fields.Char("Model Name")
    uuid = fields.Char("UUID",
                        default=lambda self: uuid.uuid4())
    timestamp = fields.Char("Timestamp",
                                default=lambda self: fields.Datetime.now())
    resource_ids = fields.Char("Resource IDs")
    raw_args_kwargs = fields.Char("Raw Args and kwargs")
    prepared_args_kwargs = fields.Char("Prepared Args and kwargs")
    context = fields.Char("Context")
    external_id = fields.Char("External ID")
    parent_log = fields.Char("Parent log")
    result = fields.Text("Result")
    remote = fields.Char("Remote")
    _sql_constraints = [
        (
            "uuid_uniq",
            "unique(uuid)",
            (
                "This UUID already exists\n"
                "Record will be skipped to avoid duplication"
            ),
        )
    ]

    def _prepare_args_kwargs(self, args, relational_model):
        # prepare args kwargs and with IDs replaed with ref(<XMLId>)
        ir_model_obj = self.env["ir.model"]
        if not args and not relational_model:
            return {}
        if isinstance(args, str):
            args = ast.literal_eval(args.strip("]["))
        if not isinstance(args, dict):
            return {}
        for k, v in args.items():
            if not v:
                continue
            res_model = ir_model_obj.search([("model", "=", relational_model)], limit=1)
            field = res_model.field_id.filtered(lambda l: l.name == k and
                                                l.ttype in ('many2one', 'one2many', 'many2many'))
            if not field:
                continue
            if field.ttype == "many2one":
                relation_model = field.relation
                rec = self.env[relation_model].browse(v)
                res = _get_external_id(rec)
                xml_id = res[rec.id] and res[rec.id][0] or False
                if not xml_id:
                    continue
                env_ref = "self.env.ref('" + xml_id + "')"
                args.update({k: env_ref})
            elif field.ttype == "one2many":
                for line in v:
                    self._prepare_args_kwargs(line[2], field.relation)
            elif field.ttype == "many2many":
                for line in v:
                    relation_model = field.relation
                    recs = self.env[relation_model].browse(line[2])
                    m2m_list = []
                    for rec in recs:
                        res = _get_external_id(rec)
                        xml_id = res[rec.id] and res[rec.id][0] or False
                        if not xml_id:
                            continue
                        env_ref = "self.env.ref('" + xml_id + "')"
                        m2m_list.append(env_ref)
                    args.update({k: [(6, 0, m2m_list)]})
        return args

    def _cron_prepare_auditlog_events(self):
        logs = self.search([("state", "=", "captured")])
        for log in logs:
            # ToDo - prepared_args_kwargs and external_id
            if not log.model_id and log.res_id:
                continue
            rec = self.env[log.model_id.model].browse(log.res_id)
            # define the global method
            res = _get_external_id(rec)
            xml_id = res[rec.id] and res[rec.id][0] or False
            args = log._prepare_args_kwargs(log.raw_args_kwargs, log.model_id.model)
            log.update(
                {
                    "external_id": xml_id,
                    "prepared_args_kwargs": args,
                    "state": "Prepared",
                }
            )
            log._cr.commit()

    def _push_event_data(self, addr, uid, password, dbname):

        log_dict = {
            "name": self.name,
            "model_name": self.model_name,
            "method": self.method,
            "uuid": self.uuid,
            "user_id": uid,
            "res_id": self.res_id,
            "log_type": self.log_type,
            "state": "Pulled",
            "timestamp": self.timestamp,
            "resource_ids": self.resource_ids,
            "prepared_args_kwargs": self.prepared_args_kwargs,
            "context": self.context,
            "external_id": self.external_id,
            "parent_log": self.parent_log,
            "remote": self.remote,
        }
        try:
            log_id = xmlrpclib.ServerProxy("%s/xmlrpc/object" % (addr)).execute(
                dbname, uid, password, "auditlog.log", "create", log_dict
            )
            self.state = "Pushed"
        except Exception as e:
            self.state = "Cancelled"
            self.result = e

    @staticmethod
    def _pull_event_data(self, addr, uid, password, dbname):
        try:
            events = xmlrpclib.ServerProxy("%s/xmlrpc/object" % (addr)).execute(
                dbname,
                uid,
                password,
                "auditlog.log",
                "search_read",
                [("state", "in", ["Prepared", "Processed"]),
                 ("user_id", "!=", uid)],
            )
        except Exception as e:
            raise ValidationError(
                _("Could not retrieve events to Pull from remote server")
            )
        for event in events:
            model_id = self.env["ir.model"].search(
                [("name", "=", event["model_id"][1])], limit=1
            )
            uuid = self.env["auditlog.log"].search(
                [("uuid", "=", event["uuid"])], limit=1
            )
            if model_id and not uuid:
                log_dict = {
                    "name": event["name"],
                    "model_id": model_id.id,
                    "method": event["method"],
                    "uuid": event["uuid"],
                    "res_id": event["res_id"],
                    "log_type": event["log_type"],
                    "state": "Pulled",
                    "timestamp": event["timestamp"],
                    "resource_ids": event["resource_ids"],
                    "prepared_args_kwargs": event["prepared_args_kwargs"],
                    "context": event["context"],
                    "external_id": event["external_id"],
                    "parent_log": event["parent_log"],
                    "remote": event["remote"],
                }
                try:
                    log_id = self.create(log_dict)
                    # commit the record before moving to next one
                    self.env.cr.commit()
                except Exception as e:
                    continue
        return

    def _cron_push_pull_event_data(self):

        server = self.env["auditlog.remote.server"].search([], limit=1)
        if server:
            addr = server.url
            userid = server.user
            password = server.password
            dbname = server.dbname
            try:
                common = xmlrpclib.ServerProxy("%s/xmlrpc/common" % (addr))
            except Exception as e:
                raise ValidationError(
                    _("Could not connect to the remote server")
                )
            try:
                uid = xmlrpclib.ServerProxy("%s/xmlrpc/common" % (addr)).authenticate(
                    dbname, userid, password, {}
                )
            except Exception as e:
                raise ValidationError(
                    _("Could not authenticate user on the remote server")
                )
            if uid:
                # Push event data that is in prepared state
                events = self.search([("state", "=", "Prepared")])
                for event in events:
                    event._push_event_data(addr, uid, password, dbname)

                # Pull event data from remote server that is in Prepared or Processed state
                self._pull_event_data(self, addr, uid, password, dbname)
        return

    def _fetch_master_data(self, model_name):
        server = self.env["auditlog.remote.server"].search([], limit=1)
        if server:
            addr = server.url
            userid = server.user
            password = server.password
            dbname = server.dbname
        try:
            uid = xmlrpclib.ServerProxy("%s/xmlrpc/common" % (addr)).authenticate(
                dbname, userid, password, {}
            )
        except Exception as e:
            raise ValidationError(
                _("Could not authenticate user on the remote server")
            )

        comodel = self.env['ir.model'].search([('model', '=', model_name)], limit=1)
        model_fields = self.env[comodel.model]._fields
        export_fields_names = []
        for ir_field in comodel.field_id:  # .filtered(lambda l: l.name not in ('id')):
            if ir_field.ttype in ('many2one', 'many2many', 'one2many'):
                field_name = '/'.join((ir_field.name, 'id'))
                export_fields_names.append(field_name)
                continue
            export_fields_names.append(ir_field.name)
        master_datas_list = []
        master_datas = False
        try:
            master_datas_list = xmlrpclib.ServerProxy("%s/xmlrpc/object" % (addr)).execute(
                dbname,
                uid,
                password,
                model_name,
                'search',
                [],
            )
        except Exception as e:
            raise ValidationError(
                _("Could not retrieve master from remote server")
            )
        try:
            master_datas = xmlrpclib.ServerProxy("%s/xmlrpc/object" % (addr)).execute(
                dbname,
                uid,
                password,
                model_name,
                'export_data',
                master_datas_list,
                export_fields_names,

            )
        except Exception as e:
            raise ValidationError(
                _("Could not export master from remote server")
            )
        return export_fields_names, master_datas

    def _cron_initialize_master_data(self):
        """Connect to remote server, and fetch all datas of the selected
        Audit Rule of type master data
        """

        log_rules = self.env['auditlog.rule'].search([('sync_type', '=', 'master'),
                                                      ('state', '=', 'subscribed')])
        auditlog_obj = self.env['auditlog.log']
        server = self.env["auditlog.remote.server"].search([], limit=1)
        if log_rules and server:
            addr = server.url
            userid = server.user
            password = server.password
            dbname = server.dbname
            try:
                common = xmlrpclib.ServerProxy("%s/xmlrpc/common" % (addr))
            except Exception as e:
                raise ValidationError(
                    _("Could not connect to the remote server")
                )
            try:
                uid = xmlrpclib.ServerProxy("%s/xmlrpc/common" % (addr)).authenticate(
                    dbname, userid, password, {}
                )
            except Exception as e:
                raise ValidationError(
                    _("Could not authenticate user on the remote server")
                )
            if uid:
                for log_rule in log_rules:
                    model_name = log_rule.model_id.model
                    mapping_fields_names, master_datas = self._fetch_master_data(model_name)
                    master_data_list = []
                    for data in master_datas.get('datas'):
                        for i in range(len(data)):
                            if isinstance(data[i], bool):
                                data[i] = str(data[i])
                        master_data_list.append(data)
                    # load the export data.
                    self.env[model_name].load(mapping_fields_names, master_data_list)
        return True

    @staticmethod
    def _populate_model_id(self, model_name):
        model_id = self.env["ir.model"].search([("model", "=", model_name)], limit=1)
        return model_id.id

    @staticmethod
    def _populate_model(self, model_id):
        model = self.env["ir.model"].search([("id", "=", model_id)], limit=1)
        model_name = model.model
        return model_name

    @api.model
    def create(self, vals):
        if vals.get("model_name") and not vals.get("model_id"):
            model = vals.get("model_name")
            vals["model_id"] = self._populate_model_id(self, model)
        if vals.get("model_id") and not vals.get("model_name"):
            model_id = vals.get("model_id")
            vals["model_name"] = self._populate_model(self, model_id)
        return super(AuditlogLog, self).create(vals)

    def write(self, vals):
        if vals.get("model") and not vals.get("model_id"):
            model = vals.get("model")
            vals["model_id"] = self._populate_model_id(self, model)
        if vals.get("model_id") and not vals.get("model"):
            model_id = vals.get("model_id")
            vals["model_name"] = self._populate_model(self, model_id)
        return super(AuditlogLog, self).write(vals)

    @staticmethod
    def _prepare_args_kwargs_to_apply(self, args_kwargs, relation_model):
        # Convert external IDs to db Ids from local system
        ir_model_obj = self.env["ir.model"]
        res_model = ir_model_obj.search([("model", "=", relation_model)], limit=1)

        if not isinstance(args_kwargs, dict):
            return args_kwargs
        for key, val in args_kwargs.items():
            if not val:
                continue
            field = res_model.field_id.filtered(lambda l: l.name == key and
                                                l.ttype in ('many2one', 'one2many', 'many2many'))
            if not field:
                continue
            if field.ttype == 'many2one':
                args_kwargs.update({key: eval(val).id})
            elif field.ttype == 'one2many':
                for line in val:
                    self._prepare_args_kwargs_to_apply(self, line[2], field.relation)
            elif field.ttype == 'many2many':
                m2m_list = []
                for lines in val:
                    m2m_ids = []
                    for line in lines[2]:
                        m2m_ids.append(eval(line).id)
                    m2m_list.append((6, 0, m2m_ids))
                args_kwargs.update({key: m2m_list})
        return args_kwargs

    def _cron_apply_event_data(self):
        events = self.search([("state", "=", "Pulled")], order="timestamp")
        for event in events:
            pulled_args_kwargs = ast.literal_eval(event.prepared_args_kwargs)
            args_kwargs = self._prepare_args_kwargs_to_apply(event,
                                                             pulled_args_kwargs,
                                                             event.model_id.model)
            event_user = event.user_id.active and event.user_id or SUPERUSER_ID
            ext_id = False
            try:
                event_object = self.env.ref(event.external_id)
                ext_id = True
            except Exception as e:
                ext_id = False
            if ext_id:
                method = getattr(event_object.with_user(event_user), event.method)
                try:
                    method(args_kwargs)
                    event.state = "Processed"
                except Exception as e:
                    event.result = str(e)
                    if event.state == "Error":
                        event.state = "Failed"
                    else:
                        event.state = "Error"
            elif event.method == "create":
                try:
                    object_id = self.env[event.model_name].with_user(event_user).create(args_kwargs)
                    event.state = "Processed"
                    ext_id = event.external_id
                    modname, rec_name = ext_id.split(".", 1)
                    ext_id_vals = {
                        "module": modname,
                        "model": event.model_name,
                        "name": rec_name,
                        "res_id": object_id,
                    }
                    self.env["ir.model.data"].create(ext_id_vals)
                except Exception as e:
                    event.result = str(e)
                    if event.state == "Error":
                        event.state = "Failed"
                    else:
                        event.state = "Error"
            self.env.cr.commit()
        return

    def reprocess_error_events(self):

        for event in self:
            if event.state not in ["Error", "Failed"]:
                continue

            pulled_args_kwargs = ast.literal_eval(event.prepared_args_kwargs)
            args_kwargs = self._prepare_args_kwargs_to_apply(event,
                                                             pulled_args_kwargs,
                                                             event.model_id.model)
            event_user = event.user_id.active and event.user_id or SUPERUSER_ID
            ext_id = False
            try:
                event_object = self.env.ref(event.external_id)
                ext_id = True
            except Exception as e:
                ext_id = False
            if ext_id:
                method = getattr(event_object.with_user(event_user), event.method)
                try:
                    method(args_kwargs)
                    event.state = "Processed"
                except Exception as e:
                    event.result = str(e)
                    event.state = "Failed"
            elif event.method == "create":
                try:
                    object_id = self.env[event.model_name].with_user(event_user).create(args_kwargs)
                    event.state = "Processed"
                    ext_id = event.external_id
                    modname, rec_name = ext_id.split(".", 1)
                    ext_id_vals = {
                        "module": modname,
                        "model": event.model_name,
                        "name": rec_name,
                        "res_id": object_id,
                    }
                    self.env["ir.model.data"].create(ext_id_vals)
                except Exception as e:
                    event.result = str(e)
                    event.state = "Failed"
        return
