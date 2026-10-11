# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.models import MAGIC_COLUMNS

from ..models.remote_odoo_match_config import (
    SUPPORTED_STORED_FIELD_DOMAIN,
    UNSUPPORTED_FIELD_TYPES,
)

_logger = logging.getLogger(__name__)


class RemoteOdooExportWizard(models.TransientModel):
    _name = "remote.odoo.export.wizard"
    _description = "Remote Odoo Export Wizard"

    model_name = fields.Char(required=True, readonly=True)
    record_ids_str = fields.Char(required=True, readonly=True)
    record_count = fields.Integer(compute="_compute_record_count")
    match_config_id = fields.Many2one("remote.odoo.match.config", readonly=True)
    instance_ids = fields.Many2many(
        "remote.odoo.instance",
        domain="[('active', '=', True)]",
        required=True,
    )
    operation = fields.Selection(
        [
            ("create_and_update", "Create and update"),
            ("create_only", "Create only"),
            ("update_only", "Update only"),
        ],
        required=True,
        default="create_and_update",
    )
    match_strategy = fields.Selection(
        [
            ("each_field_or", "Each field is an independent fallback"),
            ("all_fields_and", "All fields combined (compound key)"),
        ],
        required=True,
        default="each_field_or",
    )
    use_external_id = fields.Boolean(
        help=(
            "Look up the remote record by External ID before falling back "
            "to the match fields."
        ),
    )
    recursive_match = fields.Boolean(
        help=(
            "When a many2one field has no External ID, look up the related "
            "record on the remote using its model's match config."
        ),
    )
    override_match_field_ids = fields.Many2many(
        "ir.model.fields",
        relation="remote_odoo_export_wizard_field_rel",
        domain=SUPPORTED_STORED_FIELD_DOMAIN.replace(
            "('model_id', '=', model_id)",
            "('model_id.model', '=', model_name)",
        ),
        help=(
            "Override the match fields configured for this model just for "
            "this export."
        ),
    )
    result_text = fields.Text(readonly=True)

    @api.depends("record_ids_str")
    def _compute_record_count(self):
        for wizard in self:
            wizard.record_count = len(wizard._record_ids())

    def _record_ids(self):
        if not self.record_ids_str:
            return []
        return [int(x) for x in self.record_ids_str.split(",") if x]

    @api.model
    def open_for(self, records):
        if not records:
            raise UserError(_("No records selected."))
        config = self.env["remote.odoo.match.config"].search(
            [("model_name", "=", records._name)], limit=1
        )
        if not config:
            raise UserError(
                _("No remote export configuration found for model %s.") % records._name
            )
        return {
            "type": "ir.actions.act_window",
            "name": _("Remote Export"),
            "res_model": self._name,
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_model_name": records._name,
                "default_record_ids_str": ",".join(map(str, records.ids)),
                "default_match_config_id": config.id,
                "default_use_external_id": config.use_external_id,
                "default_recursive_match": config.recursive_match,
                "default_operation": config.operation,
                "default_match_strategy": config.match_strategy,
            },
        }

    # ---- Field selection -------------------------------------------------

    def _is_exportable_field(self, field):
        if field.name in MAGIC_COLUMNS:
            return False
        if not field.store:
            return False
        if field.compute and not field.inverse and field.readonly:
            return False
        if field.related:
            return False
        return field.type not in UNSUPPORTED_FIELD_TYPES

    def _auto_export_field_names(self, model_obj):
        names = []
        for fname, field in model_obj._fields.items():
            if not self._is_exportable_field(field):
                continue
            names.append(fname)
        return names

    def _create_field_names(self, model_obj):
        config = self.match_config_id
        if config.export_field_ids:
            return config.export_field_ids.mapped("name")
        return self._auto_export_field_names(model_obj)

    def _update_field_names(self, model_obj):
        config = self.match_config_id
        if config.update_field_ids:
            return config.update_field_ids.mapped("name")
        return self._create_field_names(model_obj)

    def _match_fields(self):
        return self.override_match_field_ids or self.match_config_id.match_field_ids

    # ---- Remote helpers --------------------------------------------------

    def _lookup_xmlid(self, instance, model_name, xmlid):
        module, name = xmlid.split(".", 1)
        imd = instance.execute_kw(
            "ir.model.data",
            "search_read",
            [
                [
                    ("module", "=", module),
                    ("name", "=", name),
                    ("model", "=", model_name),
                ]
            ],
            {"fields": ["res_id"], "limit": 1},
        )
        return imd[0]["res_id"] if imd else False

    def _resolve_remote_id(self, instance, record, _stack=None):
        """Return a remote id for a related record, or False if unknown."""
        if not record:
            return False
        xmlid = record.get_external_id().get(record.id) or None
        if xmlid:
            remote_id = self._lookup_xmlid(instance, record._name, xmlid)
            if remote_id:
                return remote_id
        if not self.recursive_match:
            return False
        target_config = self.env["remote.odoo.match.config"].search(
            [("model_name", "=", record._name)], limit=1
        )
        if not target_config or not target_config.match_field_ids:
            return False
        _stack = _stack if _stack is not None else set()
        key = (record._name, record.id)
        if key in _stack:
            return False
        _stack.add(key)
        if target_config.match_strategy == "all_fields_and":
            domain = []
            for f in target_config.match_field_ids:
                term = self._field_term_recursive(instance, record, f, _stack)
                if term is not None:
                    domain.append(term)
            if not domain:
                return False
            ids = instance.execute_kw(record._name, "search", [domain], {"limit": 2})
            return ids[0] if len(ids) == 1 else False
        for f in target_config.match_field_ids:
            term = self._field_term_recursive(instance, record, f, _stack)
            if term is None:
                continue
            ids = instance.execute_kw(record._name, "search", [[term]], {"limit": 2})
            if len(ids) == 1:
                return ids[0]
        return False

    def _field_term_recursive(self, instance, record, f, _stack):
        if f.name == "id":
            return ("id", "=", record.id)
        field = record._fields.get(f.name)
        if not field or not self._is_exportable_field(field):
            return None
        value = record[f.name]
        if field.type == "many2one":
            remote_id = (
                self._resolve_remote_id(instance, value, _stack) if value else False
            )
            return (f.name, "=", remote_id)
        return (f.name, "=", self._serialize_value(record, field))

    def _serialize_value(self, record, field):
        value = record[field.name]
        if field.type == "date":
            return fields.Date.to_string(value) if value else False
        if field.type == "datetime":
            return fields.Datetime.to_string(value) if value else False
        if value is False or value is None:
            return False
        if isinstance(value, models.BaseModel):
            raise UserError(
                _(
                    "Field %(field)s on %(model)s is relational and cannot "
                    "be sent through XML-RPC as a scalar value."
                )
                % {"field": field.name, "model": record._name}
            )
        return value

    def _missing_required_value_error(self, record, field):
        raise UserError(
            _(
                "Required field %(field)s on %(model)s(%(id)s) has no "
                "exportable value."
            )
            % {"field": field.name, "model": record._name, "id": record.id}
        )

    def _build_vals(self, instance, record, field_names, for_create=False):
        vals = {}
        for fname in field_names:
            field = record._fields.get(fname)
            if not field or not self._is_exportable_field(field):
                continue
            if field.type == "many2one":
                if record[fname]:
                    remote_id = self._resolve_remote_id(instance, record[fname])
                    if not remote_id:
                        if for_create and field.required:
                            self._missing_required_value_error(record, field)
                        # Cannot map relation, skip silently.
                        continue
                    vals[fname] = remote_id
                else:
                    if for_create and field.required:
                        self._missing_required_value_error(record, field)
                    vals[fname] = False
            else:
                value = self._serialize_value(record, field)
                if for_create and field.required and not value:
                    self._missing_required_value_error(record, field)
                vals[fname] = value
        if for_create and "name" in record._fields and not vals.get("name"):
            name_value = record.name or record.display_name
            if name_value:
                vals["name"] = name_value
        return vals

    def _field_term(self, instance, record, f):
        if f.name == "id":
            return ("id", "=", record.id)
        field = record._fields.get(f.name)
        if not field or not self._is_exportable_field(field):
            return None
        value = record[f.name]
        if field.type == "many2one":
            domain_value = self._resolve_remote_id(instance, value) if value else False
        else:
            domain_value = self._serialize_value(record, field)
        return (f.name, "=", domain_value)

    def _find_remote(self, instance, record):
        xmlid = None
        if self.use_external_id:
            xmlid = record.get_external_id().get(record.id) or None
            if xmlid:
                remote_id = self._lookup_xmlid(instance, record._name, xmlid)
                _logger.info(
                    "[%s] %s(%s) xmlid=%s -> remote=%s",
                    instance.name,
                    record._name,
                    record.id,
                    xmlid,
                    remote_id,
                )
                if remote_id:
                    return remote_id, xmlid
        match_fields = self._match_fields()
        if not match_fields:
            return False, xmlid
        if self.match_strategy == "all_fields_and":
            domain = []
            for f in match_fields:
                term = self._field_term(instance, record, f)
                if term is not None:
                    domain.append(term)
            if domain:
                ids = instance.execute_kw(
                    record._name, "search", [domain], {"limit": 2}
                )
                _logger.info(
                    "[%s] %s(%s) match AND %s -> %s",
                    instance.name,
                    record._name,
                    record.id,
                    domain,
                    ids,
                )
                if len(ids) == 1:
                    return ids[0], xmlid
            return False, xmlid
        # each_field_or: try each match field independently, in order
        for f in match_fields:
            term = self._field_term(instance, record, f)
            if term is None:
                continue
            ids = instance.execute_kw(record._name, "search", [[term]], {"limit": 2})
            _logger.info(
                "[%s] %s(%s) match OR %s -> %s",
                instance.name,
                record._name,
                record.id,
                [term],
                ids,
            )
            if len(ids) == 1:
                return ids[0], xmlid
        return False, xmlid

    def _export_one(self, instance, record, create_field_names, update_field_names):
        remote_id, xmlid = self._find_remote(instance, record)
        if remote_id:
            if self.operation == "create_only":
                return ("skipped_exists", remote_id)
            vals = self._build_vals(instance, record, update_field_names)
            instance.execute_kw(record._name, "write", [[remote_id], vals])
            return ("updated", remote_id)
        if self.operation == "update_only":
            return ("skipped_missing", False)
        vals = self._build_vals(instance, record, create_field_names, for_create=True)
        _logger.info(
            "[%s] creating %s(%s) with fields=%s name=%r",
            instance.name,
            record._name,
            record.id,
            sorted(vals),
            vals.get("name"),
        )
        new_id = instance.execute_kw(record._name, "create", [vals])
        if xmlid:
            module, name = xmlid.split(".", 1)
            instance.execute_kw(
                "ir.model.data",
                "create",
                [
                    {
                        "module": module,
                        "name": name,
                        "model": record._name,
                        "res_id": new_id,
                    }
                ],
            )
        return ("created", new_id)

    # ---- Action ----------------------------------------------------------

    def action_export(self):
        self.ensure_one()
        if not self.match_config_id:
            raise UserError(_("Missing remote export configuration."))
        if not self.use_external_id and not self._match_fields():
            raise UserError(
                _("Enable 'Use External ID' or pick at least one match " "field.")
            )
        records = self.env[self.model_name].browse(self._record_ids()).exists()
        if not records:
            raise UserError(_("No records to export."))
        model_obj = self.env[self.model_name]
        create_fields = self._create_field_names(model_obj)
        update_fields = self._update_field_names(model_obj)
        lines = []
        for instance in self.instance_ids:
            counters = {
                "created": 0,
                "updated": 0,
                "skipped_exists": 0,
                "skipped_missing": 0,
                "errors": 0,
            }
            for record in records:
                try:
                    status, _remote_id = self._export_one(
                        instance, record, create_fields, update_fields
                    )
                    counters[status] = counters.get(status, 0) + 1
                except Exception as e:
                    counters["errors"] += 1
                    _logger.exception(
                        "Remote export failed for %s id=%s on %s",
                        record._name,
                        record.id,
                        instance.name,
                    )
                    lines.append(
                        _("[%(instance)s] %(model)s(%(id)s): %(err)s")
                        % {
                            "instance": instance.name,
                            "model": record._name,
                            "id": record.id,
                            "err": e,
                        }
                    )
            lines.append(
                _(
                    "[%(instance)s] created: %(c)s, updated: %(u)s, "
                    "skipped (exists): %(se)s, skipped (missing): %(sm)s, "
                    "errors: %(e)s"
                )
                % {
                    "instance": instance.name,
                    "c": counters["created"],
                    "u": counters["updated"],
                    "se": counters["skipped_exists"],
                    "sm": counters["skipped_missing"],
                    "e": counters["errors"],
                }
            )
        self.result_text = "\n".join(lines)
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
            "context": self.env.context,
        }
