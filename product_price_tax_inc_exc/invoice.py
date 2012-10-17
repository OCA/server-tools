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


class account_invoice(Model):
    _inherit = "account.invoice"

    _columns = {
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist'),
    }

class account_invoice_line(Model):
    _inherit = "account.invoice.line"
    
    def _amount_line_tax_inc(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            price = line.price_unit * (1-(line.discount or 0.0)/100.0)
            taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, address_id=line.invoice_id.address_invoice_id, partner=line.invoice_id.partner_id)
            res[line.id] = taxes['total_included']
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        return res

    _columns = {
        'sub_total_tax_inc' : fields.function(_amount_line_tax_inc, method=True, digits_compute= dp.get_precision('Sale Price'), string='Sub-Total Tax Inc'),
    }

#TODO keep it commented for now, maybe we will use it latter
#class account_invoice_line(Model):
#    _inherit = "account.invoice.line"
#    
#    def _amount_line_tax_inc(self, cr, uid, ids, prop, unknow_none, unknow_dict):
#        res = {}
#        tax_obj = self.pool.get('account.tax')
#        cur_obj = self.pool.get('res.currency')
#        for line in self.browse(cr, uid, ids):
#            price = line.price_unit * (1-(line.discount or 0.0)/100.0)
#            taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, address_id=line.invoice_id.address_invoice_id, partner=line.invoice_id.partner_id)
#            res[line.id] = taxes['total_included']
#            if line.invoice_id:
#                cur = line.invoice_id.currency_id
#                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
#        return res

#    def _get_amount_line_tax(self, cr, uid, ids, field_name, arg, context=None):
#        invoice_obj = self.pool.get('account.invoice')
#        tax_obj = self.pool.get('account.tax')
#        res = {}
#        for line in self.browse(cr, uid, ids, context=context):
#            if line.invoice_line_tax_id:
#                res2 = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, line.price_unit, 1, product=line.product_id, address_id=line.invoice_id.address_invoice_id, partner=line.invoice_id.partner_id)
#                res[line.id] = {'price_unit_tax_exc' : res2['total'], 'price_unit_tax_inc' : res2['total_included']}
#            else:
#                res[line.id] = {'price_unit_tax_exc' : line.price_unit, 'price_unit_tax_inc' : line.price_unit}
#        return res
#    
#    _columns = {
#        'sub_total_tax_inc' : fields.function(_amount_line_tax_inc, method=True, digits_compute= dp.get_precision('Sale Price'), string='Sub-Total Tax Inc'),
#        'price_unit_tax_exc' : fields.function(_get_amount_line_tax, method=True, digits_compute= dp.get_precision('Sale Price'), string='Unit Price Tax Exc', multi='tax_val'),
#        'price_unit_tax_inc' : fields.function(_get_amount_line_tax, method=True, digits_compute= dp.get_precision('Sale Price'), string='Unit Price Tax Inc', multi='tax_val'),
#    }
