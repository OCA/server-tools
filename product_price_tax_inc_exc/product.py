# -*- encoding: utf-8 -*-
###############################################################################
#
#   product_price_tax_inc_exc for OpenERP
#   Copyright (C) 2011-TODAY Akretion <http://www.akretion.com>. All Rights Reserved
#     @author Sébastien BEAU <sebastien.beau@akretion.com>
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields
from openerp.osv.orm import Model

class product_product(Model):
    _inherit = 'product.product'

    def price_get(self, cr, uid, ids, ptype='list_price', context=None):
        if context is None:
            context = {}
        if 'tax_inc' in context:
            price_field_obj = self.pool.get('product.price.fields')
            price_field_id = price_field_obj.search(cr, uid, ['|', 
                                        ['inc_price_field_id.name', '=', ptype],
                                        ['price_field_id.name', '=', ptype],
                                        ], context=context)[0]
            price_field = price_field_obj.browse(cr, uid, price_field_id, context=context)
            if context['tax_inc']:
                ptype = price_field.inc_price_field_id.name
            else:
                ptype = price_field.price_field_id.name
        res = super(product_product, self).price_get(cr, uid, ids, ptype=ptype, context=context)
        return res
