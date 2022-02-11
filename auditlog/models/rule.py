# Copyright 2015 ABF OSIELL <https://osiell.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, modules, _

FIELDS_BLACKLIST = [
    'id', 'create_uid', 'create_date', 'write_uid', 'write_date',
    'display_name', '__last_update',
]
# Used for performance, to avoid a dictionary instanciation when we need an
# empty dict to simplify algorithms
EMPTY_DICT = {}


class DictDiffer(object):
    """Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current = set(current_dict)
        self.set_past = set(past_dict)
        self.intersect = self.set_current.intersection(self.set_past)

    def added(self):
        return self.set_current - self.intersect

    def removed(self):
        return self.set_past - self.intersect

    def changed(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] == self.current_dict[o])


class AuditlogRule(models.Model):
    _name = 'auditlog.rule'
    _description = "Auditlog - Rule"

    name = fields.Char(
        "Name", required=True,
        states={'subscribed': [('readonly', True)]})
    model_id = fields.Many2one(
        'ir.model', "Model", required=True,
        help="Select model for which you want to generate log.",
        states={'subscribed': [('readonly', True)]})
    user_ids = fields.Many2many(
        'res.users',
        'audittail_rules_users',
        'user_id', 'rule_id',
        string="Users",
        help="if  User is not added then it will applicable for all users",
        states={'subscribed': [('readonly', True)]})
    log_read = fields.Boolean(
        "Log Reads",
        help=("Select this if you want to keep track of read/open on any "
              "record of the model of this rule"),
        states={'subscribed': [('readonly', True)]})
    log_write = fields.Boolean(
        "Log Writes", default=True,
        help=("Select this if you want to keep track of modification on any "
              "record of the model of this rule"),
        states={'subscribed': [('readonly', True)]})
    log_unlink = fields.Boolean(
        "Log Deletes", default=True,
        help=("Select this if you want to keep track of deletion on any "
              "record of the model of this rule"),
        states={'subscribed': [('readonly', True)]})
    log_create = fields.Boolean(
        "Log Creates", default=True,
        help=("Select this if you want to keep track of creation on any "
              "record of the model of this rule"),
        states={'subscribed': [('readonly', True)]})
    log_type = fields.Selection(
        [('full', "Full log"),
         ('fast', "Fast log"),
         ],
        string="Type", required=True, default='full',
        help=("Full log: make a diff between the data before and after "
              "the operation (log more info like computed fields which were "
              "updated, but it is slower)\n"
              "Fast log: only log the changes made through the create and "
              "write operations (less information, but it is faster)"),
        states={'subscribed': [('readonly', True)]})
    # log_action = fields.Boolean(
    #     "Log Action",
    #     help=("Select this if you want to keep track of actions on the "
    #           "model of this rule"))
    # log_workflow = fields.Boolean(
    #     "Log Workflow",
    #     help=("Select this if you want to keep track of workflow on any "
    #           "record of the model of this rule"))
    state = fields.Selection(
        [('draft', "Draft"), ('subscribed', "Subscribed")],
        string="State", required=True, default='draft')
    action_id = fields.Many2one(
        'ir.actions.act_window', string="Action",
        states={'subscribed': [('readonly', True)]})

    _sql_constraints = [
        ('model_uniq', 'unique(model_id)',
         ("There is already a rule defined on this model\n"
          "You cannot define another: please edit the existing one."))
    ]

    def _register_hook(self):
        """Get all rules and apply them to log method calls."""
        super(AuditlogRule, self)._register_hook()
        if not hasattr(self.pool, '_auditlog_field_cache'):
            self.pool._auditlog_field_cache = {}
        if not hasattr(self.pool, '_auditlog_model_cache'):
            self.pool._auditlog_model_cache = {}
        if not self:
            self = self.search([('state', '=', 'subscribed')])
        return self._patch_methods()

    @api.multi
    def _patch_methods(self):
        """Patch ORM methods of models defined in rules to log their calls."""
        updated = False
        model_cache = self.pool._auditlog_model_cache
        for rule in self:
            if rule.state != 'subscribed':
                continue
            if not self.pool.get(rule.model_id.model):
                # ignore rules for models not loadable currently
                continue
            model_cache[rule.model_id.model] = rule.model_id.id
            model_model = self.env[rule.model_id.model]
            # CRUD
            #   -> create
            check_attr = 'auditlog_ruled_create'
            if getattr(rule, 'log_create') \
                    and not hasattr(model_model, check_attr):
                model_model._patch_method('create', rule._make_create())
                setattr(type(model_model), check_attr, True)
                updated = True
            #   -> read
            check_attr = 'auditlog_ruled_read'
            if getattr(rule, 'log_read') \
                    and not hasattr(model_model, check_attr):
                model_model._patch_method('read', rule._make_read())
                setattr(type(model_model), check_attr, True)
                updated = True
            #   -> write
            check_attr = 'auditlog_ruled_write'
            if getattr(rule, 'log_write') \
                    and not hasattr(model_model, check_attr):
                model_model._patch_method('write', rule._make_write())
                setattr(type(model_model), check_attr, True)
                updated = True
            #   -> unlink
            check_attr = 'auditlog_ruled_unlink'
            if getattr(rule, 'log_unlink') \
                    and not hasattr(model_model, check_attr):
                model_model._patch_method('unlink', rule._make_unlink())
                setattr(type(model_model), check_attr, True)
                updated = True
        return updated

    @api.multi
    def _revert_methods(self):
        """Restore original ORM methods of models defined in rules."""
        updated = False
        for rule in self:
            model_model = self.env[rule.model_id.model]
            for method in ['create', 'read', 'write', 'unlink']:
                if getattr(rule, 'log_%s' % method) and hasattr(
                        getattr(model_model, method), 'origin'):
                    model_model._revert_method(method)
                    delattr(type(model_model), 'auditlog_ruled_%s' % method)
                    updated = True
        if updated:
            modules.registry.Registry(self.env.cr.dbname).signal_changes()

    @api.model
    def create(self, vals):
        """Update the registry when a new rule is created."""
        new_record = super(AuditlogRule, self).create(vals)
        if new_record._register_hook():
            modules.registry.Registry(self.env.cr.dbname).signal_changes()
        return new_record

    @api.multi
    def write(self, vals):
        """Update the registry when existing rules are updated."""
        super(AuditlogRule, self).write(vals)
        if self._register_hook():
            modules.registry.Registry(self.env.cr.dbname).signal_changes()
        return True

    @api.multi
    def unlink(self):
        """Unsubscribe rules before removing them."""
        self.unsubscribe()
        return super(AuditlogRule, self).unlink()

    @api.multi
    def _make_create(self):
        """Instanciate a create method that log its calls."""
        self.ensure_one()
        log_type = self.log_type

        @api.model
        @api.returns('self', lambda value: value.id)
        def create_full(self, vals, **kwargs):
            self = self.with_context(auditlog_disabled=True)
            rule_model = self.env['auditlog.rule']
            new_record = create_full.origin(self, vals, **kwargs)
            new_values = dict(
                (d['id'], d) for d in new_record.sudo()
                .with_context(prefetch_fields=False).read(list(self._fields)))
            rule_model.sudo().create_logs(
                self.env.uid, self._name, new_record.ids,
                'create', None, new_values, {'log_type': log_type})
            return new_record

        @api.model
        @api.returns('self', lambda value: value.id)
        def create_fast(self, vals, **kwargs):
            self = self.with_context(auditlog_disabled=True)
            rule_model = self.env['auditlog.rule']
            vals2 = dict(vals)
            new_record = create_fast.origin(self, vals, **kwargs)
            new_values = {new_record.id: vals2}
            rule_model.sudo().create_logs(
                self.env.uid, self._name, new_record.ids,
                'create', None, new_values, {'log_type': log_type})
            return new_record

        return create_full if self.log_type == 'full' else create_fast

    @api.multi
    def _make_read(self):
        """Instanciate a read method that log its calls."""
        self.ensure_one()
        log_type = self.log_type

        def read(self, fields=None, load='_classic_read', **kwargs):
            result = read.origin(self, fields, load, **kwargs)
            # Sometimes the result is not a list but a dictionary
            # Also, we can not modify the current result as it will break calls
            result2 = result
            if not isinstance(result2, list):
                result2 = [result]
            read_values = dict((d['id'], d) for d in result2)
            # Old API

            # If the call came from auditlog itself, skip logging:
            # avoid logs on `read` produced by auditlog during internal
            # processing: read data of relevant records, 'ir.model',
            # 'ir.model.fields'... (no interest in logging such operations)
            if self.env.context.get('auditlog_disabled'):
                return result
            self = self.with_context(auditlog_disabled=True)
            rule_model = self.env['auditlog.rule']
            rule_model.sudo().create_logs(
                self.env.uid, self._name, self.ids,
                'read', read_values, None, {'log_type': log_type})
            return result
        return read

    @api.multi
    def _make_write(self):
        """Instanciate a write method that log its calls."""
        self.ensure_one()
        log_type = self.log_type

        @api.multi
        def write_full(self, vals, **kwargs):
            self = self.with_context(auditlog_disabled=True)
            rule_model = self.env['auditlog.rule']
            old_values = dict(
                (d['id'], d) for d in self.sudo()
                .with_context(prefetch_fields=False).read(list(self._fields)))
            result = write_full.origin(self, vals, **kwargs)
            new_values = dict(
                (d['id'], d) for d in self.sudo()
                .with_context(prefetch_fields=False).read(list(self._fields)))
            rule_model.sudo().create_logs(
                self.env.uid, self._name, self.ids,
                'write', old_values, new_values, {'log_type': log_type})
            return result

        @api.multi
        def write_fast(self, vals, **kwargs):
            self = self.with_context(auditlog_disabled=True)
            rule_model = self.env['auditlog.rule']
            # Log the user input only, no matter if the `vals` is updated
            # afterwards as it could not represent the real state
            # of the data in the database
            vals2 = dict(vals)
            old_vals2 = dict.fromkeys(list(vals2.keys()), False)
            old_values = dict((id_, old_vals2) for id_ in self.ids)
            new_values = dict((id_, vals2) for id_ in self.ids)
            result = write_fast.origin(self, vals, **kwargs)
            rule_model.sudo().create_logs(
                self.env.uid, self._name, self.ids,
                'write', old_values, new_values, {'log_type': log_type})
            return result

        return write_full if self.log_type == 'full' else write_fast

    @api.multi
    def _make_unlink(self):
        """Instanciate an unlink method that log its calls."""
        self.ensure_one()
        log_type = self.log_type

        @api.multi
        def unlink_full(self, **kwargs):
            self = self.with_context(auditlog_disabled=True)
            rule_model = self.env['auditlog.rule']
            old_values = dict(
                (d['id'], d) for d in self.sudo()
                .with_context(prefetch_fields=False).read(list(self._fields)))
            rule_model.sudo().create_logs(
                self.env.uid, self._name, self.ids, 'unlink', old_values, None,
                {'log_type': log_type})
            return unlink_full.origin(self, **kwargs)

        @api.multi
        def unlink_fast(self, **kwargs):
            self = self.with_context(auditlog_disabled=True)
            rule_model = self.env['auditlog.rule']
            rule_model.sudo().create_logs(
                self.env.uid, self._name, self.ids, 'unlink', None, None,
                {'log_type': log_type})
            return unlink_fast.origin(self, **kwargs)

        return unlink_full if self.log_type == 'full' else unlink_fast

    def create_logs(self, uid, res_model, res_ids, method,
                    old_values=None, new_values=None,
                    additional_log_values=None):
        """Create logs. `old_values` and `new_values` are dictionaries, e.g:
            {RES_ID: {'FIELD': VALUE, ...}}
        """
        if old_values is None:
            old_values = EMPTY_DICT
        if new_values is None:
            new_values = EMPTY_DICT
        log_model = self.env['auditlog.log']
        http_request_model = self.env['auditlog.http.request']
        http_session_model = self.env['auditlog.http.session']
        for res_id in res_ids:
            model_model = self.env[res_model]
            name = model_model.browse(res_id).name_get()
            res_name = name and name[0] and name[0][1]
            vals = {
                'name': res_name,
                'model_id': self.pool._auditlog_model_cache[res_model],
                'res_id': res_id,
                'method': method,
                'user_id': uid,
                'http_request_id': http_request_model.current_http_request(),
                'http_session_id': http_session_model.current_http_session(),
            }
            vals.update(additional_log_values or {})
            log = log_model.create(vals)
            diff = DictDiffer(
                new_values.get(res_id, EMPTY_DICT),
                old_values.get(res_id, EMPTY_DICT))
            if method is 'create':
                self._create_log_line_on_create(log, diff.added(), new_values)
            elif method is 'read':
                self._create_log_line_on_read(
                    log,
                    list(old_values.get(res_id, EMPTY_DICT).keys()), old_values
                )
            elif method is 'write':
                self._create_log_line_on_write(
                    log, diff.changed(), old_values, new_values)

    def _get_field(self, model, field_name):
        cache = self.pool._auditlog_field_cache
        if field_name not in cache.get(model.model, {}):
            cache.setdefault(model.model, {})
            # - we use 'search()' then 'read()' instead of the 'search_read()'
            #   to take advantage of the 'classic_write' loading
            # - search the field in the current model and those it inherits
            field_model = self.env['ir.model.fields']
            all_model_ids = [model.id]
            all_model_ids.extend(model.inherited_model_ids.ids)
            field = field_model.search(
                [('model_id', 'in', all_model_ids), ('name', '=', field_name)])
            # The field can be a dummy one, like 'in_group_X' on 'res.users'
            # As such we can't log it (field_id is required to create a log)
            if not field:
                cache[model.model][field_name] = False
            else:
                field_data = field.read(load='_classic_write')[0]
                cache[model.model][field_name] = field_data
        return cache[model.model][field_name]

    def _create_log_line_on_read(
            self, log, fields_list, read_values):
        """Log field filled on a 'read' operation."""
        log_line_model = self.env['auditlog.log.line']
        for field_name in fields_list:
            if field_name in FIELDS_BLACKLIST:
                continue
            field = self._get_field(log.model_id, field_name)
            # not all fields have an ir.models.field entry (ie. related fields)
            if field:
                log_vals = self._prepare_log_line_vals_on_read(
                    log, field, read_values)
                log_line_model.create(log_vals)

    def _prepare_log_line_vals_on_read(self, log, field, read_values):
        """Prepare the dictionary of values used to create a log line on a
        'read' operation.
        """
        vals = {
            'field_id': field['id'],
            'log_id': log.id,
            'old_value': read_values[log.res_id][field['name']],
            'old_value_text': read_values[log.res_id][field['name']],
            'new_value': False,
            'new_value_text': False,
        }
        if field['relation'] and '2many' in field['ttype']:
            old_value_text = self.env[field['relation']].browse(
                vals['old_value']).name_get()
            vals['old_value_text'] = old_value_text
        return vals

    def _create_log_line_on_write(
            self, log, fields_list, old_values, new_values):
        """Log field updated on a 'write' operation."""
        log_line_model = self.env['auditlog.log.line']
        for field_name in fields_list:
            if field_name in FIELDS_BLACKLIST:
                continue
            field = self._get_field(log.model_id, field_name)
            # not all fields have an ir.models.field entry (ie. related fields)
            if field:
                log_vals = self._prepare_log_line_vals_on_write(
                    log, field, old_values, new_values)
                log_line_model.create(log_vals)

    def _prepare_log_line_vals_on_write(
            self, log, field, old_values, new_values):
        """Prepare the dictionary of values used to create a log line on a
        'write' operation.
        """
        vals = {
            'field_id': field['id'],
            'log_id': log.id,
            'old_value': old_values[log.res_id][field['name']],
            'old_value_text': old_values[log.res_id][field['name']],
            'new_value': new_values[log.res_id][field['name']],
            'new_value_text': new_values[log.res_id][field['name']],
        }
        # for *2many fields, log the name_get
        if log.log_type == 'full' and field['relation'] \
                and '2many' in field['ttype']:
            # Filter IDs to prevent a 'name_get()' call on deleted resources
            existing_ids = self.env[field['relation']]._search(
                [('id', 'in', vals['old_value'])])
            old_value_text = []
            if existing_ids:
                existing_values = self.env[field['relation']].browse(
                    existing_ids).name_get()
                old_value_text.extend(existing_values)
            # Deleted resources will have a 'DELETED' text representation
            deleted_ids = set(vals['old_value']) - set(existing_ids)
            for deleted_id in deleted_ids:
                old_value_text.append((deleted_id, 'DELETED'))
            vals['old_value_text'] = old_value_text
            new_value_text = self.env[field['relation']].browse(
                vals['new_value']).name_get()
            vals['new_value_text'] = new_value_text
        return vals

    def _create_log_line_on_create(
            self, log, fields_list, new_values):
        """Log field filled on a 'create' operation."""
        log_line_model = self.env['auditlog.log.line']
        for field_name in fields_list:
            if field_name in FIELDS_BLACKLIST:
                continue
            field = self._get_field(log.model_id, field_name)
            # not all fields have an ir.models.field entry (ie. related fields)
            if field:
                log_vals = self._prepare_log_line_vals_on_create(
                    log, field, new_values)
                log_line_model.create(log_vals)

    def _prepare_log_line_vals_on_create(self, log, field, new_values):
        """Prepare the dictionary of values used to create a log line on a
        'create' operation.
        """
        vals = {
            'field_id': field['id'],
            'log_id': log.id,
            'old_value': False,
            'old_value_text': False,
            'new_value': new_values[log.res_id][field['name']],
            'new_value_text': new_values[log.res_id][field['name']],
        }
        if log.log_type == 'full' and field['relation'] \
                and '2many' in field['ttype']:
            new_value_text = self.env[field['relation']].browse(
                vals['new_value']).name_get()
            vals['new_value_text'] = new_value_text
        return vals

    @api.multi
    def subscribe(self):
        """Subscribe Rule for auditing changes on model and apply shortcut
        to view logs on that model.
        """
        act_window_model = self.env['ir.actions.act_window']
        for rule in self:
            # Create a shortcut to view logs
            domain = "[('model_id', '=', %s), ('res_id', '=', active_id)]" % (
                rule.model_id.id)
            vals = {
                'name': _("View logs"),
                'res_model': 'auditlog.log',
                'src_model': rule.model_id.model,
                'binding_model_id': rule.model_id.id,
                'domain': domain,
            }
            act_window = act_window_model.sudo().create(vals)
            rule.write({'state': 'subscribed', 'action_id': act_window.id})
        return True

    @api.multi
    def unsubscribe(self):
        """Unsubscribe Auditing Rule on model."""
        # Revert patched methods
        self._revert_methods()
        for rule in self:
            # Remove the shortcut to view logs
            act_window = rule.action_id
            if act_window:
                act_window.unlink()
        self.write({'state': 'draft'})
        return True
