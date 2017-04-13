# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models

from odoo.addons.red_october.fields import RedOctoberChar


class ResUsers(models.Model):

    _inherit = 'res.users'

    default_red_october_id = fields.Many2one(
        string='Default Crypto User',
        comodel_name='red.october.user',
        store=True,
        domain="[('id', 'in', red_october_ids)]",
        compute="_compute_default_red_october_id",
    )
    red_october_ids = fields.One2many(
        string='Crypto Users',
        comodel_name='red.october.user',
        inverse_name='user_id',
    )
    encrypted_field = RedOctoberChar(
        help='Sample encrypted item',
    )

    @api.multi
    @api.depends('red_october_ids')
    def _compute_default_red_october_id(self):
        for record in self:
            if record.default_red_october_id:
                continue
            if not record.red_october_ids:
                continue
            record.default_red_october_id = record.red_october_ids[0]
