# -*- coding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Rodo (rodo@vauxoo.com),Moy (moylop260@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import osv, fields

#TODO List:
#   *Hay que modificar la venta, para que tome en el descripción el product_code & product_name del cliente, en su pedido de venta.
#   *index to product_code
#   *Agregar contraint (analizando todas las variantes)
#   *Hacerlo multi-company (company_id & defaults)
#   *Agregar su security.csv

class product_product(osv.osv):
     _inherit = "product.product"
     
     _columns = {
          'product_customer_code_ids': fields.one2many('product.customer.code', 'product_id', 'Partner UPCs'),
     }
     
     def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=80):
          res = super(product_product, self).name_search(cr, user, name, args, operator, context, limit)
          product_partner_upc_obj=self.pool.get('product.customer.code')
          if not res:
               ids=[]
               id_prod_upc=product_partner_upc_obj.search(cr, user, [('product_code','=',name)], limit=limit, context=context)
               id_prod=id_prod_upc and product_partner_upc_obj.browse(cr, user, id_prod_upc, context=context) or []
               for ppu in id_prod:
                    ids.append(ppu.product_id.id)
               if ids:
                    res = self.name_get(cr, user, ids, context)
          return res
     
product_product()

class product_partner_upc(osv.osv):
     _name = "product.customer.code"
     _description = "Add manies UPC of Partner's"
     
     _rec_name = 'product_code'
     
     _columns = {
          'product_code': fields.char('Customer Product Code', size=64, required=True, help="This customer's product code will be used when printing a request for quotation."),
          'product_name': fields.char('Customer Product Name', size=128, help="This customer's product name will be used when printing a request for quotation. Keep empty to use the internal one."),
          'product_id': fields.many2one('product.product', 'Product', required=True),
          'partner_id': fields.many2one('res.partner', 'Partner'),
     }
product_partner_upc()
