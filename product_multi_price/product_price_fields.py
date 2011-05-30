# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    product_multi_price for OpenERP                                          #
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>   #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################

from osv import osv, fields
import netsvc
from tools.translate import _

#TODO


class product_price_fields(osv.osv):
    
    _name = "product.price.fields"
    _description = "product price fields"
    
    _columns = {
        'name': fields.related('field_id', 'field_description', type='char', size=64, string='Field Label', store=True),
        'field_name': fields.related('field_id', 'name', type='char', size=64, string='Field Name', store=True, help ="you can chose the field name by default it will be build with the name of the field replacing the space by '_' and adding x_pm_ add the start"),
        'field_id' : fields.many2one('ir.model.fields', 'Field ID', domain = [('model', '=', 'product.product'), ('ttype', '=', 'float')]),
        'sequence' : fields.integer('Sequence', help="The product 'variants' code will use order the field on the product view"),
    }

    _order = "sequence, name"

    def create(self, cr, uid, vals, context=None):
        model_id = self.pool.get('ir.model').search(cr, uid, [('model', '=', 'product.product')])[0]
        if vals.get('field_id', False):
            return super(product_price_fields, self).create(cr, uid, vals, context)
        elif vals.get('field_name', False):
            print 'field name'
            exist_id = self.pool.get('ir.model.fields').search(cr, uid, [('name', '=', vals['field_name'])])
            if exist_id:
                vals['field_id'] = exist_id[0]
                if vals.get('name', False):
                    del vals['name']
                del vals['field_name']
                return super(product_price_fields, self).create(cr, uid, vals, context)
            if vals['field_name'][0:2] != 'x_':
                raise osv.except_osv(_('User Error'), _("Please prefix the name field by x_ as it's a custom field"))

        field_vals = {
            'name': vals.get('field_name', False) or 'x_pm_' + vals['name'].replace(' ', '_'),
            'model_id':model_id,
            'model':'product.product',
            'field_description': vals['name'],
            'ttype': 'float',
            'state': 'manual'
        }
        vals['field_id'] = self.pool.get('ir.model.fields').create(cr, uid, field_vals)
        del vals['name']
        return super(product_price_fields, self).create(cr, uid, vals, context)

product_price_fields()

