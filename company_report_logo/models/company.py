# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA. (<https://opener.am>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    report_logo = fields.Binary(
        help='Logo shown in reports',
    )
