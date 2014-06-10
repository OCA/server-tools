# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2011 Camptocamp Austria (<http://www.camptocamp.at>)
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
from osv import fields, osv
import operator

def is_pair(x):
    return not x%2

def check_ean(eancode):
     if not eancode:
         return True
     if not len(eancode) in [8,12,13,14]:
         return False
     try:
         int(eancode)
     except:
         return False
     sum=0
     ean13_len= int(len(eancode))
     for i in range(ean13_len-1):
         pos=int(ean13_len-2-i)
         if is_pair(i): 
             sum += 3 * int(eancode[pos])
         else:
             sum += int(eancode[pos])
     check = 10 - operator.mod(sum,10)
     if check == 10 :
         check = 0
     if check != int(eancode[ean13_len-1]): # last digit
         return False
     return True

# need to replace the check_ean13_key function 
class product_product(osv.osv):
    _inherit = "product.product"

    def _check_ean_key(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            res = check_ean(rec.ean13)
        return res

    _columns = {
        'ean13': fields.char('EAN', help ='Code for EAN8 EAN13 UPC JPC GTIN http://de.wikipedia.org/wiki/Global_Trade_Item_Number', size=14),
    }

    _constraints = [(_check_ean_key, 'Error: Invalid EAN code', ['ean13'])]

product_product()


class product_packaging(osv.osv):
    _inherit = "product.packaging"

    def _check_ean_key(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            res = check_ean(rec.ean)
        return res

    _columns = {
        'ean':    fields.char('EAN', help ='Barcode number for EAN8 EAN13 UPC JPC GTIN', size=14),
    }
    _constraints = [(_check_ean_key, 'Error: Invalid EAN code', ['ean'])]

product_packaging()


class res_partner(osv.osv):
    _inherit = "res.partner"

    def _check_ean_key(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            res = check_ean(rec.ean13)
        return res

    _columns = {
        'ean13':    fields.char('EAN', help ='Code for EAN8 EAN13 UPC JPC GTIN http://de.wikipedia.org/wiki/Global_Trade_Item_Number', size=14),
    }

    _constraints = [(_check_ean_key, 'Error: Invalid EAN code', ['ean13'])]

res_partner()

#class wiz_ean13_check(wizard.interface):
#wiz_ean13_check()
