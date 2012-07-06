# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from tools.translate import _

class product_product(osv.osv):
    _inherit = 'product.product'

    _columns = {
        'default_code' : fields.char('Reference', size=64, required=True),
    }

    _sql_constraints = [
        ('uniq_default_code', 'unique(default_code)', "The reference must be unique"),
    ]

    _defaults = {
        'default_code': lambda * a: '/',
    }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if not 'default_code' in vals or vals['default_code'] == '/':
            vals['default_code'] = self.pool.get('ir.sequence').get(cr, uid, 'product.product')
        return super(product_product, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        products_without_code = self.search(cr, uid, [('default_code', 'in', [False, '/']),('id', 'in', ids)], context=context)
        direct_write_ids = set(ids) - set(products_without_code)
        super(product_product, self).write(cr, uid, list(direct_write_ids), vals, context)
        for product_id in products_without_code:
            vals['default_code'] = self.pool.get('ir.sequence').get(cr, uid, 'product.product')
            super(product_product, self).write(cr, uid, product_id, vals, context)
        return True

    def copy(self, cr, uid, id, default={}, context=None):
        product = self.read(cr, uid, id, ['default_code'], context=context)
        if  product['default_code']:
            default.update({
                'default_code': product['default_code']+ _('-copy'),
            })

        return super(product_product, self).copy(cr, uid, id, default, context)

product_product()
