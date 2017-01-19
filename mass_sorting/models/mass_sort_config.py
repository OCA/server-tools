# -*- coding: utf-8 -*-
# Copyright (C):
# * 2012-Today Serpent Consulting Services (<http://www.serpentcs.com>)
# * 2016-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MassSortConfig(models.Model):
    _name = 'mass.sort.config'

    # Column Section
    name = fields.Char(string='Name', translate=True, required=True)

    model_id = fields.Many2one(
        comodel_name='ir.model', string='Model', required=True)

    allow_custom_setting = fields.Boolean(
        string='Allow Custom Setting', default=True, help="If checked, any"
        " user could have the possibility to change fields, and use others.")

    one2many_field_id = fields.Many2one(
        comodel_name='ir.model.fields', string='Field to Sort', required=True,
        domain="[('model_id', '=', model_id),('ttype', '=', 'one2many')]")

    one2many_model = fields.Char(
        related='one2many_field_id.relation', readonly=True,
        string='Model Name of the Field to Sort', hel="Technical field,"
        "used in the model 'mass.sort.config.line'", store=True)

    ref_ir_act_window = fields.Many2one(
        comodel_name='ir.actions.act_window', string='Sidebar Action',
        readonly=True, copy=False)

    ref_ir_value = fields.Many2one(
        comodel_name='ir.values', string='Sidebar Button', readonly=True,
        copy=False)

    line_ids = fields.One2many(
        comodel_name='mass.sort.config.line', inverse_name='config_id',
        string='Sorting Criterias')

    # Constraint Section
    @api.constrains('one2many_field_id')
    def _check_model_sequence(self):
        field_obj = self.env['ir.model.fields']
        for config in self:
            if len(field_obj.search([
                    ('model', '=', config.one2many_field_id.relation),
                    ('name', '=', 'sequence')])) != 1:
                raise ValidationError(
                    _("The selected Field to Sort doesn't not have"
                        " 'sequence' field defined."))

    @api.constrains('model_id', 'one2many_field_id')
    def _check_model_field(self):
        for config in self:
            if config.model_id != config.one2many_field_id.model_id:
                raise ValidationError(
                    _("The selected Field to Sort '%s' doesn't belong to the"
                        " selected model '%s'.") % (
                        config.one2many_field_id.model_id.name,
                        config.model_id.name))

    @api.constrains('allow_custom_setting', 'line_ids')
    def _check_line_ids(self):
        for config in self:
            if not config.allow_custom_setting and not len(config.line_ids):
                raise ValidationError(_(
                    "You have to define field(s) in 'Sorting Criterias' if"
                    " you uncheck 'Allow Custom Setting'."))

    # Overload Section
    def unlink(self):
        self.unlink_action()
        return super(MassSortConfig, self).unlink()

    def copy(self, default=None):
        default = default or {}
        default.update({
            'name': _('%s (copy)') % self.name})
        return super(MassSortConfig, self).copy(default=default)

    # Custom Section
    @api.multi
    def create_action(self):
        action_obj = self.env['ir.actions.act_window']
        values_obj = self.env['ir.values']
        for config in self:
            button_name = _('Mass Sort (%s)') % config.name
            config.ref_ir_act_window = action_obj.create({
                'name': button_name,
                'type': 'ir.actions.act_window',
                'res_model': 'mass.sort.wizard',
                'src_model': config.model_id.model,
                'view_type': 'form',
                'context': "{'mass_sort_config_id' : %d}" % (config.id),
                'view_mode': 'form,tree',
                'target': 'new',
            })
            config.ref_ir_value = values_obj.create({
                'name': button_name,
                'model': config.model_id.model,
                'key2': 'client_action_multi',
                'value': (
                    "ir.actions.act_window,%s" % config.ref_ir_act_window.id),
            })

    @api.multi
    def unlink_action(self):
        for config in self:
            if config.ref_ir_act_window:
                config.ref_ir_act_window.unlink()
            if config.ref_ir_value:
                config.ref_ir_value.unlink()
