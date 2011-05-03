# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    product_is_a_gift for OpenERP                                          #
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
import tools
import os, sys, imp

class product_product(osv.osv):
    _inherit = "product.product"
    
    def init(self, cr):
        #load mapping for ecommerce module
        print 'launch init'
        module_2_template = {'magentoerpconnect' : 'external.mappinglines.template.csv'}
        for module in module_2_template:
            cr.execute("select id from ir_module_module where name = '%s' and state in ('installed', 'to_update');"%module)
            res = cr.fetchall()
            print 'res', res
            if res:
                filename =  module_2_template[module]
                fp = tools.file_open('product_is_a_gift/mapping/'+ filename)
                tools.convert_csv_import(cr, 'product_is_a_gift', filename , fp.read())#, idref=None, mode='init', noupdate=False)
        return True

    _columns = {
        'allow_gift_wrap': fields.boolean('Allow Gift Wrap'),
    }

    _defaults = { 'allow_gift_wrap': lambda *a: True,
    }

product_product()
