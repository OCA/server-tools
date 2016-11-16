# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) All rights reserved:
#        (c) 2012      Agile Business Group sagl (<http://www.agilebg.com>)
#        (c) 2012      Domsense srl (<http://www.domsense.com>)
#        (c) 2015      Anubía, soluciones en la nube,SL (http://www.anubia.es)
#                      Alejandro Santana <alejandrosantana@anubia.es>
#        (c) 2015      Savoir-faire Linux <http://www.savoirfairelinux.com>)
#                      Agathe Mollé <agathe.molle@savoirfairelinux.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses
#
##############################################################################

from odoo import fields, models


def _models_get(self):
    model_obj = self.env['ir.model']
    model_list = model_obj.search([])
    return [(model.model, model.name) for model in model_list]


class SuperCalendar(models.Model):
    _name = 'super.calendar'

    name = fields.Char(
        string='Description',
        required=True,
        readonly=True,
    )
    date_start = fields.Datetime(
        string='Start date',
        required=True,
        readonly=True,
    )
    duration = fields.Float(
        string='Duration',
        readonly=True,
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User',
        readonly=True,
    )
    configurator_id = fields.Many2one(
        comodel_name='super.calendar.configurator',
        string='Configurator',
        readonly=True,
    )
    res_id = fields.Reference(
        selection=_models_get,
        string='Resource',
        readonly=True,
    )
    model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Model',
        readonly=True,
    )
