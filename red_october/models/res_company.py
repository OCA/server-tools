# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ResCompany(models.Model):

    _inherit = 'res.company'

    default_red_october_id = fields.Many2one(
        string='Default Crypto Vault',
        comodel_name='red.october.vault',
        store=True,
        compute="_default_red_october_id",
        domain="[('id', 'in', red_october_ids)]",
        help='Use this Red October vault by default.',
    )
    red_october_ids = fields.Many2many(
        string='Crypto Vaults',
        comodel_name='red.october.vault',
        domain="[('company_ids', 'in', id)]",
    )

    @api.multi
    @api.depends('red_october_ids')
    def _default_default_red_october_id(self):
        for record in self:
            if record.default_red_october_id:
                continue
            if not record.red_october_ids:
                continue
            record.default_red_october_id = record.red_october_ids[0]
