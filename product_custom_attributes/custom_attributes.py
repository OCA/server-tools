# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   product_custom_attributes for OpenERP                                      #
#   Copyright (C) 2011 Akretion Benoît GUILLOT <benoit.guillot@akretion.com>  #
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

from openerp.osv.orm import Model
from openerp.osv import fields
from tools.translate import _


class attribute_group(Model):
    _inherit= "attribute.group"

    _columns = {
        'attribute_set_id': fields.many2one('attribute.set', 'Attribute Set'),
        'attribute_ids': fields.one2many('attribute.location', 'attribute_group_id', 'Attributes'),
    }

    def create(self, cr, uid, vals, context=None):
        for attribute in vals['attribute_ids']:
            if vals.get('attribute_set_id') and attribute[2] and not attribute[2].get('attribute_set_id'):
                attribute[2]['attribute_set_id'] = vals['attribute_set_id']
        return super(attribute_group, self).create(cr, uid, vals, context)

class attribute_set(Model):
    _name = "attribute.set"
    _description = "Attribute Set"
    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'attribute_group_ids': fields.one2many('attribute.group', 'attribute_set_id', 'Attribute Groups'),
        }

class attribute_location(Model):
    _name = "attribute.location"
    _description = "Attribute Location"
    _order="sequence"
    _inherits = {'custom.attribute': 'attribute_id'}


    def _get_attribute_loc_from_group(self, cr, uid, ids, context=None):
        return self.pool.get('attribute.location').search(cr, uid, [('attribute_group_id', 'in', ids)], context=context)

    _columns = {
        'attribute_id': fields.many2one('custom.attribute', 'Product Attribute', required=True, ondelete="cascade"),
        'attribute_set_id': fields.related('attribute_group_id', 'attribute_set_id', type='many2one', relation='attribute.set', string='Attribute Set', readonly=True,
store={
            'attribute.group': (_get_attribute_loc_from_group, ['attribute_set_id'], 10),
        }),
        'attribute_group_id': fields.many2one('attribute.group', 'Attribute Group', required=True),
        'sequence': fields.integer('Sequence'),
        }
