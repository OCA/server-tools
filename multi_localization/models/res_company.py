# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia - Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#


from __future__ import division, print_function, unicode_literals
from odoo import fields, models


class ResCompany(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'

    # localization_ids = fields.Many2many('ir.localization', 'ir_ui_view_localization', 'view_id', 'localization_id',
    #                                     'Localizations')
    localization_id = fields.Many2one('ir.localization', 'Localization', ondelete='restrict')
