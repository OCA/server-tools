# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

from osv import fields, osv
from crm import crm

class product_supplierinfo(osv.osv):
    _inherit = "product.supplierinfo"

    def _compute_unit_price(self, cr, uid, ids, fields, arg, context=None):
        result = {}
        for supplier in self.browse(cr, uid, ids, context=context):
            for id in supplier.pricelist_ids:
                if id.min_quantity == 1:
                    result[supplier.id] = id.price
                else:
                    result[supplier.id] = False
        return result

    _columns = {
        'unit_price': fields.function(_compute_unit_price,string='Unit Price',type='float'),
    }

product_supplierinfo()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
