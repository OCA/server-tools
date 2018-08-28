# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DependantDefaultTest(models.TransientModel):
    _name = 'dependant_default.test'

    partner_id = fields.Many2many(
        'res.partner',
        dependant_default='default_partner'
    )
    value = fields.Char(required=True)
    dependant_value = fields.Char(
        dependant_default='default_dependant_value'
    )
    dependant_integer = fields.Integer(
        dependant_default='default_dependant_integer',
        default=0
    )

    def default_partner(self, vals):
        return self.env.user.partner_id.ids

    def default_dependant_value(self, vals):
        return vals.get('value').upper()

    def default_dependant_integer(self, vals):
        return len(vals.get('value'))
