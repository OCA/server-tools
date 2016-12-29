# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia - Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from odoo import fields, models


class ResUsers(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    localization_id = fields.Many2one('ir.localization', 'Localization', ondelete='restrict')
