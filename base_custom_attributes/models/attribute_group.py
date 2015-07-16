# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   base_attribute.attributes for OpenERP                                     #
#   Copyright (C) 2011 Akretion Benoît GUILLOT <benoit.guillot@akretion.com>  #
#   Copyright (C) 2013 Akretion Raphaël VALYI <raphael.valyi@akretion.com>    #
#   Copyright (C) 2015 Savoir-faire Linux                                     #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

from openerp import models, fields, api


class AttributeGroup(models.Model):
    _name = "attribute.group"
    _description = "Attribute Group"
    _order = "sequence"

    name = fields.Char(
        'Name',
        size=128,
        required=True,
        translate=True
    )

    sequence = fields.Integer('Sequence')

    attribute_set_id = fields.Many2one(
        'attribute.set',
        'Attribute Set'
    )

    attribute_ids = fields.One2many(
        'attribute.location',
        'attribute_group_id',
        'Attributes'
    )

    def _get_default_model(self):
        force_model = self.env.context.get('force_model')

        if force_model:
            models = self.env['ir.model'].search([
                ('model', '=', force_model)])

            if models:
                return models[0]

        return False

    model_id = fields.Many2one(
        'ir.model',
        'Model',
        required=True,
        default=_get_default_model,
    )

    @api.model
    def create(self, vals):
        for attribute in vals.get('attribute_ids', []):
            if (
                vals.get('attribute_set_id') and
                attribute[2] and
                not attribute[2].get('attribute_set_id')
            ):
                attribute[2]['attribute_set_id'] = vals['attribute_set_id']

        return super(AttributeGroup, self).create(vals)
