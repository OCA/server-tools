# coding: utf-8
# © 2018 David BEAL @ Akretion
# © 2018 Mourad EL HADJ MIMOUNE @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import ast

from odoo import _, api, fields, models
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, ValidationError


class OnchangeRuleLine(models.TransientModel):
    _name = 'onchange.rule.line'
    _description = "Onchange Rule Lines"
    _order = 'sequence'

    onchange_rule_id = fields.Many2one(
        comodel_name='onchange.rule', string="Onchange Rules", required=True)
    model_id = fields.Many2one(
        comodel_name='ir.model',
        related='onchange_rule_id.model_id',
        help="")
    onchange_field_id = fields.Many2one(
        comodel_name='ir.model.fields', string="Onchange Field",
        required=True)
    implied_model = fields.Char(
        related='onchange_field_id.relation', string="Implied Model",
        help="")
    implied_record = fields.Reference(
        selection='_authorised_implied_models', required=True,
        help="Select the object that'll execute onchange.")
    sequence = fields.Integer()
    dest_field_id = fields.Many2one(
        string="Destination Field",
        comodel_name='ir.model.fields',
        required=True,
        help="Select field that'll be driven by onchange "
             "according to implied record.")
    dest_val_type = fields.Selection(
        string="Value Type",
        selection=[
            ("fixed", "Fixed"),
            ("related", "Related")],
        help="Destination value type")
    dest_selection_value = fields.Char(
        string="Selection Value",
        # selection='_compute_destination_value',
        help="Final select value after onchange is executed")
    dest_m2o_value = fields.Reference(
        selection='_authorised_destination_models', string="M2O Value",
        help="Final value after onchange is executed (Many2one)")
    dest_related_field = fields.Char(
        string="Destination Related Field",
        help="Related value is used to apply the onchange value get"
             " form related fields.\nE.g.: on sale order we can apply"
             " the partner price list by using this notation:"
             " partner_id.price_list_id")
    readonly = fields.Boolean(
        help="If checked ensure than record can't be updated by user "
             "(only by inserted data)")
    is_restrictive_rule = fields.Boolean(
        string="Restrictive Rule",
        help="Restrictive rule is used to force the value of destination "
             "field.\nIf restrictive rule is False, destination value "
             "is set as default and can be modified by user", )
    onchange_warning = fields.Text(string="Warning")
    onchange_domain = fields.Char(
        string="Domain",
        help="Domain is used in on_change. Domain must be in this form:"
             " {'partner_id': [('name', '=', 'Akretion')]}")

    CRITICAL_FIELDS = ['model_id', 'onchange_field_id']

    @api.model
    def create(self, vals):
        res = super(OnchangeRuleLine, self).create(vals)
        self.onchange_rule_id._update_registry()
        return res

    @api.multi
    def write(self, vals):
        res = super(OnchangeRuleLine, self).write(vals)
        if set(vals).intersection(self.CRITICAL_FIELDS):
            self.onchange_rule_id._update_registry()
        return res

    @api.model
    def _authorised_implied_models(self):
        # can be used to restrict use of some models
        domain = [('onchange_rule_unavailable', '=', False)]
        if self.onchange_field_id.relation:
            domain.append(('name', '=', self.onchange_field_id.relation))
        models = self.env['ir.model'].search(domain, order='name')
        return [(x.model, x.name) for x in models]

    @api.model
    def _authorised_destination_models(self):
        # can be used to restrict use of some models
        domain = [('onchange_rule_unavailable', '=', False)]
        if self.dest_field_id.relation:
            domain.append(('name', '=', self.dest_field_id.relation))
        models = self.env['ir.model'].search(domain)
        return [(x.model, x.name) for x in models]

    @api.multi
    @api.onchange('onchange_field_id')
    def _compute_implied_record(self):
        for rec in self:
            if rec.onchange_field_id.relation:
                last = self.env[rec.onchange_field_id.relation].search(
                    [], order='id desc', limit=1)
                rec.implied_record = last

    @api.multi
    @api.onchange('dest_val_type')
    def _onchange_dest_val_type(self):
        for rec in self:
            if rec.dest_val_type == 'fixed':
                rec.dest_related_field = False
            elif rec.dest_val_type == 'related':
                rec.dest_m2o_value = False
                rec.dest_selection_value = False

    @api.multi
    @api.onchange('dest_field_id')
    def _compute_destination_value(self):
        self.ensure_one()
        if self.dest_field_id.relation:
            last = self.env[self.dest_field_id.relation].search(
                [], order='id desc', limit=1)
            self.dest_m2o_value = last
        if self.dest_field_id.ttype == 'selection':
            select_vals = self.env[
                self.dest_field_id.model_id.model].fields_get()[
                self.dest_field_id.name]['selection']
            return select_vals
        return

    @api.constrains('dest_related_field', 'model_id')
    def _check_des_related_field(self):
        """ Ensuring that the related field exists and
        it corresponding to the destination field relation """
        for rule_line in self:
            model_name = rule_line.model_id.model
            model_obj = self.env[model_name]
            if not rule_line.dest_related_field:
                continue
            related_field = rule_line.dest_related_field
            try:
                local_dict = {'obj': model_obj}
                related_model = safe_eval(
                    "obj.%s" % related_field, local_dict)
                if related_model._name != rule_line.dest_field_id.relation:
                    msg = ('The related field model ("%s") is different from '
                           'the destination fiield relation ("%s")' %
                           (related_model._name,
                            rule_line.dest_field_id.relation))
                    raise ValidationError(msg)
            except UserError as err:
                # constrains should raise ValidationError exceptions
                raise ValidationError(err)

    @api.constrains('onchange_domain')
    def _check_des_field_domain(self):
        """ Ensuring that the domain is for destination field relation """
        for rule_line in self:
            model_obj = self.env[rule_line.model_id.model]
            if not rule_line.onchange_domain:
                continue
            try:
                onchange_domain = ast.literal_eval(
                    self.onchange_domain or "{}")
                for domain_field, domain in onchange_domain.items():
                    comodel_name = model_obj._fields[domain_field].comodel_name
                    if not comodel_name:
                        msg = 'The field "%s" is not a relational field' %\
                            domain_field
                        raise ValidationError(msg)
                    model_obj[domain_field].search(domain)
            except UserError as err:
                # constrains should raise ValidationError exceptions
                raise ValidationError(err)

    @api.constrains('dest_selection_value')
    def _check_dest_selection_value(self):
        """ Ensure that the dest_selection_value is in destination
        fields selection """
        for rule_line in self:
            if rule_line.dest_field_id.ttype == 'selection':
                select_vals = self.env[
                    rule_line.dest_field_id.model_id.model].fields_get()[
                    rule_line.dest_field_id.name]['selection']
                if rule_line.dest_selection_value\
                        not in [s[0] for s in select_vals]:
                    raise ValidationError(
                        _('The value "%s" you chose for the destination '
                          'selection field "%s" is wrong.'
                          ' Value must be in this list %s')
                        % (rule_line.dest_selection_value,
                           rule_line.dest_field_id.name,
                           select_vals)
                    )

    @api.constrains('dest_m2o_value')
    def _check_dest_m2o_value(self):
        """ Ensure that the dest_m2o_value exite an correspending to
         dest_field_id.relation model"""
        for rule_line in self:
            if rule_line.dest_field_id.relation:
                if rule_line.dest_m2o_value and \
                        rule_line.dest_m2o_value._name != \
                        rule_line.dest_field_id.relation:
                    raise ValidationError(
                        _('The value "%s" of the destination '
                          'one2many field "%s" doesn''t exist in model "%s". '
                          'Choose an existing value')
                        % (rule_line.dest_m2o_value,
                           rule_line.dest_field_id.name,
                           self.env[rule_line.dest_field_id.relation].
                            _description)
                    )

    @api.multi
    def _get_onchange_value(self):
        result = {}
        self.ensure_one()
        onchange_self = self.env.context.get('onchange_self')
        for rule_line in self:
            dest_val = False
            domain = ast.literal_eval(self.onchange_domain or "{}")
            if rule_line.dest_val_type == 'fixed':
                if rule_line.dest_field_id.relation:
                    dest_val = rule_line.dest_m2o_value.id
                else:
                    dest_val = rule_line.dest_selection_value
            elif rule_line.dest_val_type == 'related':
                dest_val = safe_eval(
                    "obj.%s" % rule_line.dest_related_field, {
                        'obj': onchange_self})
            if rule_line.implied_record == onchange_self[
                    rule_line.onchange_field_id.name]:
                result['value'] = {rule_line.dest_field_id.name: dest_val}
                domain = self._get_domain_for_restrictive_rule()
                if domain:
                    result['domain'] = domain
                if rule_line.onchange_warning:
                    result['warning'] = {
                        'title': _('Rule Error ! %s') %
                        rule_line.onchange_rule_id.name,
                        'message': rule_line.onchange_warning,
                    }
        return result

    @api.model
    def _get_domain_for_restrictive_rule(self):
        result = ast.literal_eval(self.onchange_domain or "{}")
        if self.is_restrictive_rule:
            if self.dest_field_id.relation and self.dest_m2o_value:
                field_domain = {self.dest_field_id.name: [
                    ('id', '=', self.dest_m2o_value.id),
                ]}
                if not result:
                    result = field_domain
                elif self.dest_field_id.name not in result:
                    result.update(field_domain)
                else:
                    domain = result[self.dest_field_id.name] or []
                    result[self.dest_field_id.name] = domain.apend(
                        ('id', '=', self.dest_m2o_value.id))
        return result

    def _get_restrictive_rule_line(self, records):
        """ Return the onchange restrictive rule.
        The returned actions' context contain an object to manage processing.
        """
        if '__onchange_action_done' not in self._context:
            self = self.with_context(__onchange_action_done={})
        domain = [('onchange_rule_id.model_id.model', '=', records._name),
                  ('is_restrictive_rule', '=', True)]
        rule_lines = self.env['onchange.rule.line'].with_context(
            active_test=True).search(domain)
        return rule_lines.with_env(self.env)

    def button_duplicate_record(self):
        self.ensure_one()
        record = self.copy()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'onchange.rule',
            'target': 'current',
            'view_mode': 'form',
            'res_id': record.onchange_rule_id.id,
        }
