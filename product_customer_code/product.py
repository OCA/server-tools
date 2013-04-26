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
from openerp.osv import osv, fields
from openerp.tools.translate import _


class product_product(osv.Model):
    _inherit = "product.product"

    _columns = {
        'product_customer_code_ids': fields.one2many('product.customer.code',
                                                     'product_id',
                                                     'Customer Codes'),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default['product_customer_code_ids'] = False
        res = super(product_product, self).copy(
            cr, uid, id, default=default, context=context)
        return res

    def name_search(self, cr, user, name='', args=None, operator='ilike',
                    context=None, limit=80):
        res = super(product_product, self).name_search(
            cr, user, name, args, operator, context, limit)
        if not context:
            context = {}
        product_customer_code_obj = self.pool.get('product.customer.code')
        if not res:
            ids = []
            partner_id = context.get('partner_id', False)
            if partner_id:
                id_prod_code = \
                        product_customer_code_obj.search(cr, user,
                                                         [('product_code',
                                                                '=', name),
                                                         ('partner_id', '=',
                                                                 partner_id)],
                                                         limit=limit,
                                                         context=context)
                # TODO: Search for product customer name
                id_prod = id_prod_code and product_customer_code_obj.browse(
                    cr, user, id_prod_code, context=context) or []
                for ppu in id_prod:
                    ids.append(ppu.product_id.id)
            if ids:
                res = self.name_get(cr, user, ids, context)
        return res
