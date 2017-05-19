# coding: utf-8
# © 2017 David BEAL @ Akretion
# © 2017 Mourad EL HADJ MIMOUNE @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from odoo import api, fields, models
from odoo.modules.registry import Registry

import logging
_logger = logging.getLogger(__name__)


class OnchangeRule(models.Model):
    _name = "onchange.rule"

    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get()

    name = fields.Char(required=True)
    active = fields.Boolean(
        default=True,
        help="The active field allows you to make your record "
             "without effect but without remove it.")
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', index=1,
        default=_default_company)
    model_id = fields.Many2one(
        comodel_name='ir.model', string='Model', required=True,
        help="")
    sequence = fields.Integer()
    rule_line_ids = fields.One2many(
        comodel_name='onchange.rule.line', inverse_name='onchange_rule_id',
        string='Onchange Rule Lines')
    exist_restrictive_line = fields.Boolean(
        compute="_compute_exist_restrictive_line")

    CRITICAL_FIELDS = ['model_id', 'active']

    @api.multi
    @api.depends('rule_line_ids.is_restrictive_rule')
    def _compute_destination_value(self):
        for rec in self:
            if rec.rule_line_ids.filtered('is_restrictive_rule'):
                rec.exist_restrictive_line = True

    @api.model
    def create(self, vals):
        res = super(OnchangeRule, self).create(vals)
        self._update_registry()
        return res

    @api.multi
    def write(self, vals):
        res = super(OnchangeRule, self).write(vals)
        if set(vals).intersection(self.CRITICAL_FIELDS):
            self._update_registry()
        return res

    @api.multi
    def unlink(self):
        res = super(OnchangeRule, self).unlink()
        self._update_registry()
        return res

    def _update_registry(self):
        """ Update the registry after a modification on action rules. """
        if self.env.registry.ready and not self.env.context.get('import_file'):
            # for the sake of simplicity, simply force the registry to reload
            self._cr.commit()
            self.env.reset()
            registry = Registry.new(self._cr.dbname)
            registry.signal_registry_change()

    def _process(self, records):
        """ Process action ``self`` on the ``records``
        that have not been done yet. """
        # filter out the records on which self has already been done
        action_done = self._context['__onchange_action_done']
        records_done = action_done.get(self, records.browse())
        records -= records_done
        if not records:
            return
        # mark the remaining records as done (to avoid recursive processing)
        action_done = dict(action_done)
        action_done[self] = records_done + records
        self = self.with_context(__onchange_action_done=action_done)
        records = records.with_context(__onchange_action_done=action_done)

        # modify records
        values = {}
        for rule_line in self.rule_line_ids.filtered('is_restrictive_rule'):
            to_update_records = records.filtered(
                lambda rev: rev[rule_line.onchange_field_id.name] ==
                rule_line.implied_record)
            if to_update_records and\
                    rule_line.dest_field_id.name in records._fields:
                dest_val = False
                if rule_line.dest_field_id.relation:
                    dest_val = rule_line.m2o_value.id
                else:
                    dest_val = rule_line.dest_selection_value
                if dest_val:
                    values[rule_line.dest_field_id.name] = dest_val
                to_update_records.write(values)

    @api.model_cr
    def _register_hook(self):
        """ Patch models that should trigger action rules based on creation,
            modification of records and form onchanges.
        """
        def make_create():
            """ Instanciate a create method that processes action rules. """
            @api.model
            def create(self, vals, **kw):
                # retrieve the action rules to possibly execute
                onchange_rules = self.env['onchange.rule.line'].\
                    _get_restrictive_rule_line(self)
                # call original method
                record = create.origin(
                    self.with_env(onchange_rules.env), vals, **kw)
                # check postconditions, and execute onchange_rules
                # on the records that satisfy them
                for rule in onchange_rules.with_context(old_values=None):
                    rule.onchange_rule_id._process(record)
                return record.with_env(self.env)

            return create

        def make_write():
            """ Instanciate a _write method that processes action rules. """
            #
            # Note: we patch method _write() instead of write() in order to
            # catch updates made by field recomputations.
            #
            @api.multi
            def _write(self, vals, **kw):
                # retrieve the onchange rules to possibly execute
                onchange_rules = self.env['onchange.rule.line'].\
                    _get_restrictive_rule_line(self)
                # call original method
                records = self.with_env(onchange_rules.env)
                # check preconditions on records
                # read old values before the update
                old_values = {
                    old_vals.pop('id'): old_vals
                    for old_vals in records.read(list(vals))
                }
                # call original method
                _write.origin(records, vals, **kw)
                # check postconditions, and execute actions
                # on the records that satisfy them
                for rule in onchange_rules.with_context(old_values=old_values):
                    rule.onchange_rule_id._process(records)
                return True

            return _write

        def make_onchange(onchange_rule_line_id):
            """ Instanciate an onchange method for the given action rule. """
            def base_onchange_rule_onchange(self):
                result = {}
                onchange_rule_line = self.env['onchange.rule.line'].\
                    browse(onchange_rule_line_id)
                res = onchange_rule_line.with_context(
                    active_model=self._name, onchange_self=self
                )._get_onchange_value()
                if res:
                    if 'value' in res:
                        res['value'].pop('id', None)
                        self.update(
                            {key: val for key, val in
                             res['value'].iteritems() if key in self._fields})
                    if 'domain' in res:
                        result.setdefault('domain', {}).update(res['domain'])
                    if 'warning' in res:
                        result['warning'] = res['warning']
                return result

            return base_onchange_rule_onchange

        patched_models = defaultdict(set)

        def patch(model, name, method):
            """ Patch method `name` on `model`,
             unless it has been patched already. """
            if model not in patched_models[name]:
                patched_models[name].add(model)
                model._patch_method(name, method)

        # retrieve all onchange rule, and patch their corresponding model
        for onchange_rule in self.with_context({}).search([]):
            Model = self.env[onchange_rule.model_id.model]
            patch_create_write = False
            for rule_line in onchange_rule.rule_line_ids:
                # register an onchange method for the onchange_rule
                method = make_onchange(rule_line.id)
                if rule_line.onchange_field_id:
                    field_name = rule_line.onchange_field_id.name
                    Model._onchange_methods[field_name.strip()].append(method)
                if rule_line.is_restrictive_rule:
                    patch_create_write = True

            if patch_create_write:
                patch(Model, 'create', make_create())
                patch(Model, '_write', make_write())

    @api.model
    def _get_rules_from_model(self, model_name):
        model = self.env['ir.model'].search([('model', '=', model_name)])
        return self.env['onchange.rule'].search(
            [('model_id', '=', model.id)])
