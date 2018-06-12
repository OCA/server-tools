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

from odoo import models, fields


class AttributeLocation(models.Model):
    _name = "attribute.location"
    _description = "Attribute Location"
    _order = "sequence"
    _inherits = {'attribute.attribute': 'attribute_id'}

    attribute_id = fields.Many2one(
        'attribute.attribute',
        'Product Attribute',
        required=True,
        ondelete="cascade"
    )

    attribute_set_id = fields.Many2one(
        'attribute.set',
        'Attribute Set',
        related='attribute_group_id.attribute_set_id',
        readonly=True
    )

    attribute_group_id = fields.Many2one(
        'attribute.group',
        'Attribute Group',
        required=True,
        ondelete="cascade"
    )

    sequence = fields.Integer('Sequence')
