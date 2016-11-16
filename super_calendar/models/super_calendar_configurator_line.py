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


class SuperCalendarConfiguratorLine(models.Model):
    _name = 'super.calendar.configurator.line'

    name = fields.Many2one(
        comodel_name='ir.model',
        string='Model',
        required=True,
    )
    domain = fields.Char(
        string='Domain',
    )
    configurator_id = fields.Many2one(
        comodel_name='super.calendar.configurator',
        string='Configurator',
    )
    description_type = fields.Selection(
        [('field', 'Field'),
         ('code', 'Code')],
        string="Description Type",
        default='field',
    )
    description_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Description field',
        domain="[('ttype', 'in', ('char', 'text')), ('model_id', '=', name)]",
    )
    description_code = fields.Text(
        string='Description field',
        help=("""Use '${o}' to refer to the involved object.
E.g.: '${o.project_id.name}'"""),
    )
    date_start_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Start date field',
        domain="[('ttype', 'in', ('datetime', 'date')), "
               "('model_id', '=', name)]",
        required=True,
    )
    date_stop_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='End date field',
        domain="[('ttype', 'in', ('datetime', 'date')), "
               "('model_id', '=', name)]",
    )
    duration_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Duration field',
        domain="[('ttype', '=', 'float'), ('model_id', '=', name)]",
    )
    user_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='User field',
        domain="[('ttype', '=', 'many2one'), ('model_id', '=', name)]",
    )
