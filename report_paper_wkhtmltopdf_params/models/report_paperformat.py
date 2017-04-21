# -*- coding: utf-8 -*-
# Copyright 2017 Avoin.Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class Paper(models.Model):
    _inherit = 'report.paperformat'

    disable_smart_shrinking = fields.Boolean(
        'Disable Smart Shrinking',
        help='Disable the intelligent shrinking strategy '
             'used by WebKit that makes the pixel/dpi '
             'ratio none constant.'
    )

    custom_params = fields.One2many(
        'report.paperformat.parameter',
        'paperformat_id',
        'Custom Parameters',
        help='Custom Parameters passed forward as wkhtmltopdf '
             'command arguments'
    )
