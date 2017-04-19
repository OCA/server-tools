# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    default_address_validate_id = fields.Many2one(
        string='Default Address Validator',
        comodel_name='address.validate',
        domain="[('company_ids', 'in', id)]",
    )
