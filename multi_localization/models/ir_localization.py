# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia
# Copyright 2016 Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#


from odoo import fields, models


class IrLocalization(models.Model):
    _name = 'ir.localization'
    _order = 'name'

    name = fields.Char(translate=True)
    country_id = fields.Many2one('res.country', string='Country')
    lang_id = fields.Many2one('res.lang', string='Language')
