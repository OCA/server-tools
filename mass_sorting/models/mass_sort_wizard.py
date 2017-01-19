# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MassSortWizard(models.TransientModel):
    _name = 'mass.sort.wizard'

    # Default Section
    def _default_config_id(self):
        return self._context.get('mass_sort_config_id', False)

    def _default_line_ids(self):
        config_obj = self.env['mass.sort.config']
        line_ids = []
        config = config_obj.browse(
            self._context.get('mass_sort_config_id', False))
        if config:
            for line in config.line_ids:
                line_ids.append((0, 0, {
                    'sequence': line.sequence,
                    'field_id': line.field_id.id,
                    'desc': line.desc}))
        return line_ids

    # Column Section
    config_id = fields.Many2one(
        comodel_name='mass.sort.config', default=_default_config_id,
        required=True)

    description = fields.Text(
        string='Description', readonly=True, compute='_compute_description')

    allow_custom_setting = fields.Boolean(
        string='Allow Custom Setting', readonly=True,
        related='config_id.allow_custom_setting')

    one2many_model = fields.Char(
        string='Model Name of the Field to Sort', readonly=True,
        related='config_id.one2many_model')

    line_ids = fields.One2many(
        comodel_name='mass.sort.wizard.line', inverse_name='wizard_id',
        string='Sorting Criterias', default=_default_line_ids)

    # Compute Section
    @api.depends('config_id')
    def _compute_description(self):
        for wizard in self:
            wizard.description = _(
                "You will sort the field '%(field)s' for %(qty)d %(model)s(s)"
                ". \n\nThe sorting will be done by %(field_list)s.") % ({
                    'field':
                    wizard.config_id.one2many_field_id.field_description,
                    'qty': len(self._context.get('active_ids', False)),
                    'model': wizard.config_id.model_id.name,
                    'field_list': ', '.join(
                        [x.field_id.field_description
                            for x in wizard.line_ids])
                    })

    # Constraint Section
    @api.constrains('line_ids')
    def _check_line_ids(self):
        for wizard in self:
            if not len(wizard.line_ids):
                raise ValidationError(_(
                    "Please Select at least one Sorting Criteria."))

    # Action Section
    def button_apply(self):
        self.ensure_one()
        wizard = self
        active_ids = self._context.get('active_ids')

        model_obj = self.env[wizard.config_id.model_id.model]
        one2many_obj = self.env[wizard.config_id.one2many_field_id.relation]
        parent_field = wizard.config_id.one2many_field_id.relation_field

        order_list = []
        for line in wizard.line_ids:
            order_list.append(
                line.desc and
                '%s desc' % line.field_id.name or line.field_id.name)
        order = ', '.join(order_list)

        for item in model_obj.browse(active_ids):
            # DB Query sort by the correct order
            lines = one2many_obj.search(
                [(parent_field, '=', item.id)], order=order)

            # Write new sequence to sort lines
            sequence = 1
            for line in lines:
                line.sequence = sequence
                sequence += 1
