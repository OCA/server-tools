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
import decimal_precision as dp
from tools.translate import _
from invoice_sale import InvoiceSale, InvoiceSaleLine

class sale_order(InvoiceSale):
    _inherit = "sale.order"

    _columns = {
        'tax_inc' : fields.boolean('Tax Inc', help="Tic the box if you want to use unit price in taxe include"),
    }

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        result = super(sale_order, self)._prepare_invoice(cr, uid, order, lines, context=context)
        result['tax_inc'] = order.tax_inc
        return result


class sale_order_line(InvoiceSaleLine):
    _inherit = "sale.order.line"

    def _get_amount_line_tax(self, cr, uid, ids, field_name, arg, context=None):
        order_obj = self.pool.get('sale.order')
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            amount_tax_line = order_obj._amount_line_tax(cr, uid, line, context=None)
            res[line.id] = amount_tax_line + line.price_subtotal
        return res
    
    _columns = {
        'sub_total_tax_inc' : fields.function(_get_amount_line_tax, method=True, digits_compute= dp.get_precision('Sale Price'), string='Sub-Total Tax Inc'),
    }

#TODO keep it commented for now, maybe we will use it latter

#    def _get_amount_line_tax(self, cr, uid, ids, field_name, arg, context=None):
#        order_obj = self.pool.get('sale.order')
#        tax_obj = self.pool.get('account.tax')
#        res = {}
#        for line in self.browse(cr, uid, ids, context=context):
#            res[line.id] = {'amount_tax_line' : order_obj._amount_line_tax(cr, uid, line, context=None)}
#            res[line.id]['sub_total_tax_inc'] = res[line.id]['amount_tax_line'] + line.price_subtotal
#            if line.tax_id:
#                res2 = tax_obj.compute_all(cr, uid, line.tax_id, line.price_unit, 1, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)
#                print 'res2', res2
#                res[line.id]['price_unit_tax_exc'] = res2['total']
#                res[line.id]['price_unit_tax_inc'] = res2['total_included']
#        return res
#    
#    _columns = {
#        'amount_tax_line' : fields.function(_get_amount_line_tax, method=True, digits_compute= dp.get_precision('Sale Price'), string='Taxes Amount', multi='tax_val'),
#        'sub_total_tax_inc' : fields.function(_get_amount_line_tax, method=True, digits_compute= dp.get_precision('Sale Price'), string='Sub-Total Tax Inc', multi='tax_val'),
#        'price_unit_tax_exc' : fields.function(_get_amount_line_tax, method=True, digits_compute= dp.get_precision('Sale Price'), string='Unit Price Tax Exc', multi='tax_val'),
#        'price_unit_tax_inc' : fields.function(_get_amount_line_tax, method=True, digits_compute= dp.get_precision('Sale Price'), string='Unit Price Tax Inc', multi='tax_val'),
#    }
