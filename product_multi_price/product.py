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



class product_product(osv.osv):
    
    _inherit = "product.product"

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        result = super(osv.osv, self).fields_view_get(cr, uid, view_id,view_type,context,toolbar=toolbar, submenu=submenu)
        if view_type=='form':
            product_price_fields_obj = self.pool.get('product.price.fields')
            product_price_fields_ids = product_price_fields_obj.search(cr, uid, [], context=context)
            price_fields = [x.field_name for x in product_price_fields_obj.browse(cr, uid, product_price_fields_ids, context=context)]
            result['fields'].update(self.fields_get(cr, uid, price_fields, context))
            arch = u''
            for field in price_fields:
                arch += '<field name="' + field +'"/>'
            result['arch'] = result['arch'].decode('utf8').replace('<field name="list_price" modifiers="{}"/>', arch)
#            print result
        return result

product_product()

