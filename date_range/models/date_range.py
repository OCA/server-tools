# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class DateRange(models.Model):
    _name = "date.range"

    name = fields.Char(required=True, translate=True)
    date_start = fields.Datetime(required=True)
    date_end = fields.Datetime(required=True)
    type_id = fields.Many2one(
        comodel_name='date.range.type', string='Type', select=1, required=True)
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', select=1)
    active = fields.Boolean(
        help="The active field allows you to hide the date range without "
        "removing it.")
