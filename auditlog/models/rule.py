# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ABF OSIELL (<http://osiell.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, modules, _, SUPERUSER_ID, sql_db

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


class auditlog_rule(models.Model):
    _name = 'auditlog.rule'
    _description = "Auditlog - Rule"

    name = fields.Char(u"Name", size=32, required=True)
    model_id = fields.Many2one(
        'ir.model', u"Model", required=True,
        help=u"Select model for which you want to generate log.")
    user_ids = fields.Many2many(
        'res.users',
        'audittail_rules_users',
        'user_id', 'rule_id',
        string=u"Users",
        help=u"if  User is not added then it will applicable for all users")
    log_read = fields.Boolean(
        u"Log Reads",
        help=(u"Select this if you want to keep track of read/open on any "
              u"record of the model of this rule"))
    log_write = fields.Boolean(
        u"Log Writes", default=True,
        help=(u"Select this if you want to keep track of modification on any "
              u"record of the model of this rule"))
    log_unlink = fields.Boolean(
        u"Log Deletes", default=True,
        help=(u"Select this if you want to keep track of deletion on any "
              u"record of the model of this rule"))
    log_create = fields.Boolean(
        u"Log Creates", default=True,
        help=(u"Select this if you want to keep track of creation on any "
              u"record of the model of this rule"))
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
        string=u"State", required=True, default='draft')
    action_id = fields.Many2one(
        'ir.actions.act_window', string="Action")

    _sql_constraints = [
        ('model_uniq', 'unique(model_id)',
         ("There is already a rule defined on this model\n"
          "You cannot define another: please edit the existing one."))
    ]

    def _register_hook(self, cr, ids=None):
        """Get all rules and apply them to log method calls."""
        super(auditlog_rule, self)._register_hook(cr)
        if not hasattr(self.pool, '_auditlog_field_cache'):
            self.pool._auditlog_field_cache = {}
        if not hasattr(self.pool, '_auditlog_model_cache'):
            self.pool._auditlog_model_cache = {}
        if ids is None:
            ids = self.search(cr, SUPERUSER_ID, [('state', '=', 'subscribed')])
        return self._patch_methods(cr, SUPERUSER_ID, ids)

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
                model_model._patch_method('create', self._make_create())
                setattr(model_model, check_attr, True)
                updated = True
            #   -> read
            check_attr = 'auditlog_ruled_read'
            if getattr(rule, 'log_read') \
                    and not hasattr(model_model, check_attr):
                model_model._patch_method('read', self._make_read())
                setattr(model_model, check_attr, True)
                updated = True
            #   -> write
            check_attr = 'auditlog_ruled_write'
            if getattr(rule, 'log_write') \
                    and not hasattr(model_model, check_attr):
                model_model._patch_method('write', self._make_write())
                setattr(model_model, check_attr, True)
                updated = True
            #   -> unlink
            check_attr = 'auditlog_ruled_unlink'
            if getattr(rule, 'log_unlink') \
                    and not hasattr(model_model, check_attr):
                model_model._patch_method('unlink', self._make_unlink())
                setattr(model_model, check_attr, True)
                updated = True
        return updated

    @api.multi
    def _revert_methods(self):
        """Restore original ORM methods of models defined in rules."""
        updated = False
        for rule in self:
            model_model = self.env[rule.model_id.model]
            for method in ['create', 'read', 'write', 'unlink']:
                if getattr(rule, 'log_%s' % method):
                    model_model._revert_method(method)
                    updated = True
        if updated:
            modules.registry.RegistryManager.signal_registry_change(
                self.env.cr.dbname)

    # Unable to find a way to declare the `create` method with the new API,
    # errors occurs with the `_register_hook()` BaseModel method.
    def create(self, cr, uid, vals, context=None):
        """Update the registry when a new rule is created."""
        res_id = super(auditlog_rule, self).create(
            cr, uid, vals, context=context)
        if self._register_hook(cr, [res_id]):
            modules.registry.RegistryManager.signal_registry_change(cr.dbname)
        return res_id

    # Unable to find a way to declare the `write` method with the new API,
    # errors occurs with the `_register_hook()` BaseModel method.
    def write(self, cr, uid, ids, vals, context=None):
        """Update the registry when existing rules are updated."""
        if isinstance(ids, (int, long)):
            ids = [ids]
        super(auditlog_rule, self).write(cr, uid, ids, vals, context=context)
        if self._register_hook(cr, ids):
            modules.registry.RegistryManager.signal_registry_change(cr.dbname)
        return True

    def _make_create(self):
        """Instanciate a create method that log its calls."""
        @api.model
        def create(self, vals, **kwargs):
            rule_model = self.env['auditlog.rule']
            new_record = create.origin(self, vals, **kwargs)
            new_values = dict(
                (d['id'], d) for d in new_record.sudo().read(
                    list(self._columns)))
            rule_model.sudo().create_logs(
                self.env.uid, self._name, new_record.ids,
                'create', None, new_values)
            return new_record
        return create

    def _make_read(self):
        """Instanciate a read method that log its calls."""

        def read(self, *args, **kwargs):
            result = read.origin(self, *args, **kwargs)
            # Sometimes the result is not a list but a dictionary
            # Also, we can not modify the current result as it will break calls
            result2 = result
            if not isinstance(result2, list):
                result2 = [result]
            read_values = dict((d['id'], d) for d in result2)
            # Old API
            if args and isinstance(args[0], sql_db.Cursor):
                cr, uid, ids = args[0], args[1], args[2]
                if isinstance(ids, (int, long)):
                    ids = [ids]
                env = api.Environment(cr, uid, {})
                rule_model = env['auditlog.rule']
                rule_model.sudo().create_logs(
                    env.uid, self._name, ids,
                    'read', read_values)
            # New API
            else:
                rule_model = self.env['auditlog.rule']
                rule_model.sudo().create_logs(
                    self.env.uid, self._name, self.ids,
                    'read', read_values)
            return result
        return read

    def _make_write(self):
        """Instanciate a write method that log its calls."""
        @api.multi
        def write(self, vals, **kwargs):
            rule_model = self.env['auditlog.rule']
            old_values = dict(
                (d['id'], d) for d in self.sudo().read(list(self._columns)))
            result = write.origin(self, vals, **kwargs)
            new_values = dict(
                (d['id'], d) for d in self.sudo().read(list(self._columns)))
            rule_model.sudo().create_logs(
                self.env.uid, self._name, self.ids,
                'write', old_values, new_values)
            return result
        return write

    def _make_unlink(self):
        """Instanciate an unlink method that log its calls."""
        @api.multi
        def unlink(self, **kwargs):
            rule_model = self.env['auditlog.rule']
            old_values = dict(
                (d['id'], d) for d in self.sudo().read(list(self._columns)))
            rule_model.sudo().create_logs(
                self.env.uid, self._name, self.ids, 'unlink', old_values)
            return unlink.origin(self, **kwargs)
        return unlink

    def create_logs(self, uid, res_model, res_ids, method,
                    old_values=None, new_values=None,
                    additional_log_values=None):
        """Create logs. `old_values` and `new_values` are dictionnaries, e.g:
            {RES_ID: {'FIELD': VALUE, ...}}
        """
        if old_values is None:
            old_values = EMPTY_DICT
        if new_values is None:
            new_values = EMPTY_DICT
        log_model = self.env['auditlog.log']
        for res_id in res_ids:
            model_model = self.env[res_model]
            # Avoid recursivity with the 'read' method called by 'name_get()'
            res_name = "%s,%s" % (res_model, res_id)
            if method is not 'read':
                name = model_model.browse(res_id).name_get()
                res_name = name and name[0] and name[0][1] or res_name
            vals = {
                'name': res_name,
                'model_id': self.pool._auditlog_model_cache[res_model],
                'res_id': res_id,
                'method': method,
                'user_id': uid,
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
                    log, old_values.get(res_id, EMPTY_DICT).keys(), old_values)
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
        if field['relation'] and '2many' in field['ttype']:
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
        if field['relation'] and '2many' in field['ttype']:
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
        model_data_model = self.env['ir.model.data']
        for rule in self:
            # Create a shortcut to view logs
            domain = "[('model_id', '=', %s), ('res_id', '=', active_id)]" % (
                rule.model_id.id)
            vals = {
                'name': _(u"View logs"),
                'res_model': 'auditlog.log',
                'src_model': rule.model_id.model,
                'domain': domain,
            }
            act_window = act_window_model.sudo().create(vals)
            rule.write({'state': 'subscribed', 'action_id': act_window.id})
            keyword = 'client_action_relate'
            value = 'ir.actions.act_window,%s' % act_window.id
            model_data_model.sudo().ir_set(
                'action', keyword, 'View_log_' + rule.model_id.model,
                [rule.model_id.model], value, replace=True,
                isobject=True, xml_id=False)
        return True

    @api.multi
    def unsubscribe(self):
        """Unsubscribe Auditing Rule on model."""
        act_window_model = self.env['ir.actions.act_window']
        ir_values_model = self.env['ir.values']
        # Revert patched methods
        self._revert_methods()
        for rule in self:
            # Remove the shortcut to view logs
            act_window = act_window_model.search(
                [('name', '=', 'View Log'),
                 ('res_model', '=', 'auditlog.log'),
                 ('src_model', '=', rule.model_id.model)])
            if act_window:
                value = 'ir.actions.act_window,%s' % act_window.id
                act_window.unlink()
                ir_value = ir_values_model.search(
                    [('model', '=', rule.model_id.model),
                     ('value', '=', value)])
                if ir_value:
                    ir_value.unlink()
        self.write({'state': 'draft'})
        return True
