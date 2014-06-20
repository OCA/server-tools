# -*- coding: utf-8 -*-
##############################################################################
#
#    Product GTIN module for OpenERP
#    Copyright (C) 2004-2011 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2011 Camptocamp (<http://www.camptocamp.at>)
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

from openerp.osv import orm, fields
import operator


def is_pair(x):
    return not x % 2


def check_ean(eancode):
    if not eancode:
        return True
    if not len(eancode) in [8, 12, 13, 14]:
        return False
    try:
        int(eancode)
    except:
        return False
    sum = 0
    ean13_len = int(len(eancode))
    for i in range(ean13_len-1):
        pos = int(ean13_len-2-i)
        if is_pair(i):
            sum += 3 * int(eancode[pos])
        else:
            sum += int(eancode[pos])
    check = 10 - operator.mod(sum, 10)
    if check == 10:
        check = 0
    if check != int(eancode[ean13_len-1]):  # last digit
        return False
    return True


class product_product(orm.Model):
    _inherit = "product.product"

    def _check_ean_key(self, cr, uid, ids):
        for rec in self.browse(cr, uid, ids):
            if not check_ean(rec.ean13):
                return False
        return True

    _columns = {
        'ean13': fields.char(
            'EAN', size=14,
            help="Code for EAN8 EAN13 UPC JPC GTIN "
            "http://en.wikipedia.org/wiki/Global_Trade_Item_Number"),
    }

    _constraints = [(_check_ean_key, 'Error: Invalid EAN code', ['ean13'])]


class product_packaging(orm.Model):
    _inherit = "product.packaging"

    def _check_ean_key(self, cr, uid, ids):
        for rec in self.browse(cr, uid, ids):
            if not check_ean(rec.ean):
                return False
        return True

    _columns = {
        'ean': fields.char(
            'EAN', size=14,
            help='Barcode number for EAN8 EAN13 UPC JPC GTIN'),
        }

    _constraints = [(_check_ean_key, 'Error: Invalid EAN code', ['ean'])]


class res_partner(orm.Model):
    _inherit = "res.partner"

    def _check_ean_key(self, cr, uid, ids):
        for rec in self.browse(cr, uid, ids):
            if not check_ean(rec.ean13):
                return False
        return True

    _columns = {
        'ean13': fields.char(
            'EAN', size=14,
            help="Code for EAN8 EAN13 UPC JPC GTIN "
            "http://en.wikipedia.org/wiki/Global_Trade_Item_Number"),
        }

    _constraints = [(_check_ean_key, 'Error: Invalid EAN code', ['ean13'])]
