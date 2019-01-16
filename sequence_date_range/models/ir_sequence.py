# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    date_range_field = fields.Selection(
        selection=[
            ('date_from', 'From'),
            ('date_to', 'To'),
        ],
        required=True,
        default="date_from",
        help="Define which date field must be used in case of date ranges as "
             "the reference date to generate sequences.\n"
             "Ex: date_from = '2018-10-01' and date_to = '2019-09-30'.\n"
             "If you pick 'date_to' as reference date, your range_year will "
             "be 2019 (2018 if you pick the 'date_from', who is the default)",
    )
