# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, tools
from odoo.osv import expression


class IrRule(models.Model):
    _inherit = 'ir.rule'

    and_rule = fields.Boolean(
        help='Whether this group rule should be applied as an AND operation',
    )

    @api.model
    @tools.ormcache('self._uid', 'model_name', 'mode')
    def _compute_domain(self, model_name, mode='read'):
        domain = super(IrRule, self)._compute_domain(model_name, mode)
        domains_to_AND = self.sudo().search([
            ('model_id.model', '=', model_name),
            ('and_rule', '=', True),
            ('global', '=', False),
        ]).mapped('domain')
        if domains_to_AND:
            domain = expression.AND(domain + domains_to_AND)
        return domain
