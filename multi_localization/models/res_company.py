# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia
# Copyright 2016 Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#


from odoo import fields, models


class ResCompany(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'

    localization_id = fields.Many2one('ir.localization', 'Localization',
                                      ondelete='restrict')
