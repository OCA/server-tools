# -*- coding: utf-8 -*-
# © 2015 Guewen Baconnier (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class IrModel(models.Model):
    _inherit = 'ir.model'

    @api.multi
    def _compute_has_an_active_field(self):
        for model in self:
            active_fields = self.env['ir.model.fields'].search(
                [('model_id', '=', model.id),
                 ('name', '=', 'active'),
                 ],
                limit=1)
            model.has_an_active_field = bool(active_fields)

    @api.model
    def _search_has_an_active_field(self,  operator, value):
        if operator not in ['=', '!=']:
            raise AssertionError('operator %s not allowed' % operator)
        fields_model = self.env['ir.model.fields']
        domain = []
        active_fields = fields_model.search(
            [('name', '=', 'active')])
        models = active_fields.mapped('model_id')
        if operator == '=' and value or operator == '!=' and not value:
            domain.append(('id', 'in', models.ids))
        else:
            domain.append(('id', 'not in', models.ids))
        return domain

    has_an_active_field = fields.Boolean(
        compute=_compute_has_an_active_field,
        search=_search_has_an_active_field,
        string='Has an active field',
    )
