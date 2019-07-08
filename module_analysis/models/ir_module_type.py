# Copyright (C) 2019-Today: GRAP (<http://www.grap.coop/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class IrModuleType(models.Model):
    _name = 'ir.module.type'
    _description = 'Modules Types'
    _order = 'sequence'

    name = fields.Char(string='Name', required=True)

    sequence = fields.Integer(string='Sequence')

    module_ids = fields.One2many(
        string='Modules', comodel_name='ir.module.module',
        inverse_name='module_type_id')

    module_qty = fields.Integer(
        string='Modules Quantity', compute='_compute_module_qty', store=True)

    @api.multi
    @api.depends('module_ids.module_type_id')
    def _compute_module_qty(self):
        for module_type in self:
            module_type.module_qty = len(module_type.module_ids)
