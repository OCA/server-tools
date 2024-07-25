# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
try:
    import odoorpc
except:
    logging.error('Unable to import odoorpc')
import psycopg2
import traceback
from urlparse import urlparse
from openerp import _, api, exceptions, fields, models, tools
from collections import namedtuple


import_context_tuple = namedtuple(
    'import_context', [
        'remote', 'model_line', 'ids', 'idmap', 'dummies', 'dummy_instances',
        'to_delete', 'field_context',
    ]
)


class ImportContext(import_context_tuple):
    def with_field_context(self, *args):
        return ImportContext(*(self[:-1] + (field_context(*args),)))


field_context = namedtuple(
    'field_context', ['record_model', 'field_name', 'record_id'],
)


mapping_key = namedtuple('mapping_key', ['model_name', 'remote_id'])


dummy_instance = namedtuple(
    'dummy_instance', ['model_name', 'field_name', 'remote_id', 'dummy_id'],
)


class ImportOdooDatabase(models.Model):
    _name = 'import.odoo.database'
    _description = 'An Odoo database to import'

    url = fields.Char(required=True)
    database = fields.Char(required=True)
    user = fields.Char(default='admin', required=True)
    password = fields.Char(default='admin')
    import_line_ids = fields.One2many(
        'import.odoo.database.model', 'database_id', string='Import models',
    )
    import_field_mappings = fields.One2many(
        'import.odoo.database.field', 'database_id', string='Field mappings',
    )
    cronjob_id = fields.Many2one(
        'ir.cron', string='Import job', readonly=True, copy=False,
    )
    cronjob_running = fields.Boolean(compute='_compute_cronjob_running')
    status_data = fields.Serialized('Status', readonly=True, copy=False)
    status_html = fields.Html(
        compute='_compute_status_html', readonly=True, sanitize=False,
    )

    @api.multi
    def action_import(self):
        """Create a cronjob to run the actual import"""
        self.ensure_one()
        if self.cronjob_id:
            return self.cronjob_id.write({
                'numbercall': 1,
                'doall': True,
                'active': True,
            })
        return self.write({
            'cronjob_id': self._create_cronjob().id,
        })

    @api.multi
    def _run_import(self, commit=True, commit_threshold=100):
        """Run the import as cronjob, commit often"""
        self.ensure_one()
        if not self.password:
            return
        # model name: [ids]
        remote_ids = {}
        # model name: count
        remote_counts = {}
        # model name: count
        done = {}
        # mapping_key: local_id
        idmap = {}
        # mapping_key: local_id
        # this are records created or linked when we need to fill a required
        # field, but the local record is not yet created
        dummies = {}
        # model name: [local_id]
        # this happens when we create a dummy we can throw away again
        to_delete = {}
        # dummy_instance
        dummy_instances = []
        remote = self._get_connection()
        self.write({'password': False})
        if commit and not tools.config['test_enable']:
            # pylint: disable=invalid-commit
            self.env.cr.commit()
        for model_line in self.import_line_ids:
            model = model_line.model_id
            remote_ids[model.model] = remote.execute(
                model.model, 'search',
                tools.safe_eval(model_line.domain) if model_line.domain else []
            )
            remote_counts[model.model] = len(remote_ids[model.model])
        self.write({
            'status_data': {
                'counts': remote_counts,
                'ids': remote_ids,
                'error': None,
                'done': {},
            }
        })
        if commit and not tools.config['test_enable']:
            # pylint: disable=invalid-commit
            self.env.cr.commit()
        for model_line in self.import_line_ids:
            model = self.env[model_line.model_id.model]
            done[model._name] = 0
            chunk_len = commit and (commit_threshold or 1) or len(
                remote_ids[model._name]
            )

            for start_index in range(
                    len(remote_ids[model._name]) / chunk_len + 1
            ):
                index = start_index * chunk_len
                ids = remote_ids[model._name][index:index + chunk_len]
                context = ImportContext(
                    remote, model_line, ids, idmap, dummies, dummy_instances,
                    to_delete, field_context(None, None, None),
                )
                try:
                    self._run_import_model(context)
                except:
                    error = traceback.format_exc()
                    self.env.cr.rollback()
                    self.write({
                        'status_data': dict(self.status_data, error=error),
                    })
                    # pylint: disable=invalid-commit
                    self.env.cr.commit()
                    raise
                done[model._name] += len(ids)
                self.write({'status_data': dict(self.status_data, done=done)})
                if commit and not tools.config['test_enable']:
                    # pylint: disable=invalid-commit
                    self.env.cr.commit()

    @api.multi
    def _run_import_model(self, context):
        """Import records of a configured model"""
        model = self.env[context.model_line.model_id.model]
        fields = self._run_import_model_get_fields(context)
        recompute_ids = []
        for data in context.remote.execute(
                model._name, 'read', context.ids, fields.keys()
        ):
            self._run_import_get_record(context, model, data)
            if (model._name, data['id']) in context.idmap:
                # there's a mapping for this record, nothing to do
                continue
            data = self._run_import_map_values(context, data)
            _id = data['id']
            record = self._create_record(context, model, data)
            recompute_ids.append(record.id)
            self._run_import_model_cleanup_dummies(
                context, model, _id, record.id,
            )
        to_recompute = model.browse(recompute_ids)
        for field in model._fields.values():
            if not field.compute:
                continue
            to_recompute._recompute_todo(field)
        to_recompute.recompute()

    @api.multi
    def _create_record(self, context, model, record):
        """Create a record, add an xmlid"""
        _id = record.pop('id')
        xmlid = '%d-%s-%d' % (
            self.id, model._name.replace('.', '_'), _id,
        )
        if self.env.ref('base_import_odoo.%s' % xmlid, False):
            new = self.env.ref('base_import_odoo.%s' % xmlid)
            with self.env.norecompute():
                new.with_context(
                    **self._create_record_context(model, record)
                ).write(record)
        else:
            with self.env.norecompute():
                new = model.with_context(
                    **self._create_record_context(model, record)
                ).create(record)
            self.env['ir.model.data'].create({
                'name': xmlid,
                'model': model._name,
                'module': 'base_import_odoo',
                'res_id': new.id,
                'noupdate': True,
                'import_database_id': self.id,
                'import_database_record_id': _id,
            })
        context.idmap[mapping_key(model._name, _id)] = new.id
        return new

    def _create_record_context(self, model, record):
        """Return a context that is used when creating a record"""
        context = {
            'tracking_disable': True,
        }
        if model._name == 'res.users':
            context['no_reset_password'] = True
        return context

    @api.multi
    def _run_import_get_record(
        self, context, model, record, create_dummy=True,
    ):
        """Find the local id of some remote record. Create a dummy if not
        available"""
        _id = context.idmap.get((model._name, record['id']))
        if not _id:
            _id = context.dummies.get((model._name, record['id']))
            if _id:
                context.dummy_instances.append(
                    dummy_instance(*(context.field_context + (_id,)))
                )
        if not _id:
            _id = self._run_import_get_record_mapping(
                context, model, record, create_dummy=create_dummy,
            )
        if not _id:
            xmlid = self.env['ir.model.data'].search([
                ('import_database_id', '=', self.id),
                ('import_database_record_id', '=', record['id']),
                ('model', '=', model._name),
            ], limit=1)
            if xmlid:
                _id = xmlid.res_id
                context.idmap[(model._name, record['id'])] = _id
        if not _id and create_dummy:
            _id = self._run_import_create_dummy(context, model, record)
        return _id

    @api.multi
    def _run_import_get_record_mapping(
        self, context, model, record, create_dummy=True,
    ):
        current_field = self.env['ir.model.fields'].search([
            ('name', '=', context.field_context.field_name),
            ('model_id.model', '=', context.field_context.record_model),
        ])
        mappings = self.import_field_mappings.filtered(
            lambda x:
            x.mapping_type == 'fixed' and
            x.model_id.model == model._name and
            (
                not x.field_ids or current_field in x.field_ids
            ) and x.local_id and
            (x.remote_id == record['id'] or not x.remote_id) or
            x.mapping_type == 'by_field' and
            x.model_id.model == model._name
        )
        _id = None
        for mapping in mappings:
            if mapping.mapping_type == 'fixed':
                assert mapping.local_id
                _id = mapping.local_id
                context.idmap[(model._name, record['id'])] = _id
                break
            elif mapping.mapping_type == 'by_field':
                assert mapping.field_ids
                if len(record) == 1:
                    continue
                records = model.search([
                    (field.name, '=', record[field.name])
                    for field in mapping.field_ids
                ], limit=1)
                if records:
                    _id = records.id
                    context.idmap[(model._name, record['id'])] = _id
                    break
            else:
                raise exceptions.UserError(_('Unknown mapping'))
        return _id

    @api.multi
    def _run_import_create_dummy(
        self, context, model, record, forcecreate=False,
    ):
        """Either misuse some existing record or create an empty one to satisfy
        required links"""
        dummy = model.search([
            (
                'id', 'not in',
                [
                    v for (model_name, remote_id), v
                    in context.dummies.items()
                    if model_name == model._name
                ] +
                [
                    mapping.local_id for mapping
                    in self.import_field_mappings
                    if mapping.model_id.model == model._name and
                    mapping.local_id
                ]
            ),
        ], limit=1)
        if dummy and not forcecreate:
            context.dummies[mapping_key(model._name, record['id'])] = dummy.id
            context.dummy_instances.append(
                dummy_instance(*(context.field_context + (dummy.id,)))
            )
            return dummy.id
        required = [
            name
            for name, field in model._fields.items()
            if field.required
        ]
        defaults = model.default_get(required)
        values = {'id': record['id']}
        for name, field in model._fields.items():
            if name not in required or name in defaults:
                continue
            value = None
            if field.type in ['char', 'text', 'html']:
                value = ''
            elif field.type in ['boolean']:
                value = False
            elif field.type in ['integer', 'float']:
                value = 0
            elif model._fields[name].type in ['date', 'datetime']:
                value = '2000-01-01'
            elif field.type in ['many2one']:
                new_context = context.with_field_context(
                    model._name, name, record['id']
                )
                value = self._run_import_get_record(
                    new_context,
                    self.env[model._fields[name].comodel_name],
                    {'id': record.get(name, [None])[0]},
                )
            elif field.type in ['selection'] and not callable(field.selection):
                value = field.selection[0][0]
            elif field.type in ['selection'] and callable(field.selection):
                value = field.selection(model)[0][0]
            values[name] = value
        dummy = self._create_record(context, model, values)
        context.dummies[mapping_key(model._name, record['id'])] = dummy.id
        context.to_delete.setdefault(model._name, [])
        context.to_delete[model._name].append(dummy.id)
        context.dummy_instances.append(
            dummy_instance(*(context.field_context + (dummy.id,)))
        )
        return dummy.id

    @api.multi
    def _run_import_map_values(self, context, data):
        model = self.env[context.model_line.model_id.model]
        for field_name in data.keys():
            if not isinstance(
                    model._fields[field_name], fields._Relational
            ) or not data[field_name]:
                continue
            if model._fields[field_name].type == 'one2many':
                # don't import one2many fields, use an own configuration
                # for this
                data.pop(field_name)
                continue
            ids = data[field_name] if (
                model._fields[field_name].type != 'many2one'
            ) else [data[field_name][0]]
            new_context = context.with_field_context(
                model._name, field_name, data['id']
            )
            comodel = self.env[model._fields[field_name].comodel_name]
            data[field_name] = [
                self._run_import_get_record(
                    new_context, comodel, {'id': _id},
                    create_dummy=model._fields[field_name].required or
                    any(
                        m.model_id._name == comodel._name
                        for m in self.import_line_ids
                    ),
                )
                for _id in ids
            ]
            data[field_name] = filter(None, data[field_name])
            if model._fields[field_name].type == 'many2one':
                if data[field_name]:
                    data[field_name] = data[field_name] and data[field_name][0]
                else:
                    data[field_name] = None
            else:
                data[field_name] = [(6, 0, data[field_name])]
        for mapping in self.import_field_mappings:
            if mapping.model_id.model != model._name:
                continue
            if mapping.mapping_type == 'unique':
                for field in mapping.field_ids:
                    value = data.get(field.name, '')
                    counter = 1
                    while model.with_context(active_test=False).search([
                        (field.name, '=', data.get(field.name, value)),
                    ]):
                        data[field.name] = '%s (%d)' % (value, counter)
                        counter += 1
            elif mapping.mapping_type == 'by_reference':
                res_model = data.get(mapping.model_field_id.name)
                res_id = data.get(mapping.id_field_id.name)
                update = {
                    mapping.model_field_id.name: None,
                    mapping.id_field_id.name: None,
                }
                if res_model in self.env.registry and res_id:
                    new_context = context.with_field_context(
                        model._name, res_id, data['id']
                    )
                    record_id = self._run_import_get_record(
                        new_context, self.env[res_model], {'id': res_id},
                        create_dummy=False
                    )
                    if record_id:
                        update.update({
                            mapping.model_field_id.name: res_model,
                            mapping.id_field_id.name: record_id,
                        })
                data.update(update)
        return data

    @api.multi
    def _run_import_model_get_fields(self, context):
        return {
            name: field
            for name, field
            in self.env[context.model_line.model_id.model]._fields.items()
            if not field.compute or field.related
        }

    @api.multi
    def _run_import_model_cleanup_dummies(
            self, context, model, remote_id, local_id
    ):
        for instance in context.dummy_instances:
            if (
                    instance.model_name != model._name or
                    instance.remote_id != remote_id
            ):
                continue
            if not context.idmap.get(instance.remote_id):
                continue
            model = self.env[instance.model_name]
            record = model.browse(context.idmap[instance.remote_id])
            field_name = instance.field_id.name
            if record._fields[field_name].type == 'many2one':
                record.write({field_name: local_id})
            elif record._fields[field_name].type == 'many2many':
                record.write({field_name: [
                    (3, context.idmap[remote_id]),
                    (4, local_id),
                ]})
            else:
                raise exceptions.UserError(
                    _('Unhandled field type %s') %
                    record._fields[field_name].type
                )
            context.dummy_instances.remove(instance)
            dummy_id = context.dummies[(record._model, remote_id)]
            if dummy_id in context.to_delete:
                model.browse(dummy_id).unlink()
            del context.dummies[(record._model, remote_id)]

    def _get_connection(self):
        self.ensure_one()
        url = urlparse(self.url)
        hostport = url.netloc.split(':')
        if len(hostport) == 1:
            hostport.append('80')
        host, port = hostport
        remote = odoorpc.ODOO(
            host,
            protocol='jsonrpc+ssl' if url.scheme == 'https' else 'jsonrpc',
            port=int(port),
        )
        remote.login(self.database, self.user, self.password)
        return remote

    @api.constrains('url', 'database', 'user', 'password')
    @api.multi
    def _constrain_url(self):
        for this in self:
            if this == self.env.ref('base_import_odoo.demodb', False):
                continue
            if tools.config['test_enable']:
                continue
            if not this.password:
                continue
            this._get_connection()

    @api.depends('status_data')
    @api.multi
    def _compute_status_html(self):
        for this in self:
            if not this.status_data:
                continue
            this.status_html = self.env.ref(
                'base_import_odoo.view_import_odoo_database_qweb'
            ).render({'object': this})

    @api.depends('cronjob_id')
    @api.multi
    def _compute_cronjob_running(self):
        for this in self:
            if not this.cronjob_id:
                continue
            try:
                with self.env.cr.savepoint():
                    self.env.cr.execute(
                        'select id from "%s" where id=%%s for update nowait' %
                        self.env['ir.cron']._table,
                        (this.cronjob_id.id,), log_exceptions=False,
                    )
            except psycopg2.OperationalError:
                this.cronjob_running = True

    @api.multi
    def _create_cronjob(self):
        self.ensure_one()
        return self.env['ir.cron'].create({
            'name': self.display_name,
            'model': self._name,
            'function': '_run_import',
            'doall': True,
            'args': str((self.ids,)),
        })

    @api.multi
    def name_get(self):
        return [
            (this.id, '%s@%s, %s' % (this.user, this.url, this.database))
            for this in self
        ]
