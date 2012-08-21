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

from openerp.osv.orm import TransientModel
from osv import fields


class open_product_by_attribute_set(TransientModel):
    _name = 'open.product.by.attribute.set'
    _description = 'Wizard to open product by attributes set'

    _columns = {
        'attribute_set_id':fields.many2one('attribute.set', 'Attribute Set'),
        }

    def open_product_by_attribute(self, cr, uid, ids, context=None):
        """
        Opens Product by attributes
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of account chart’s IDs
        @return: dictionary of Product list window for a given attributes set
        """
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        if context is None:
            context = {}
        attribute_set = self.browse(cr, uid, ids[0], context=context).attribute_set_id
        data = self.read(cr, uid, ids, [], context=context)[0] # XXX used?
        result = mod_obj.get_object_reference(cr, uid, 'product', 'product_normal_action')
        id = result[1] if result else False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        result['context'] = "{'set_id': %s, 'open_product_by_attribute_set': %s}"%(attribute_set.id, True)
        result['domain'] = "[('attribute_set_id', '=', %s)]" % attribute_set.id
        result['name'] = attribute_set.name
        return result


