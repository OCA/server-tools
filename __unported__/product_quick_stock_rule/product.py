# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   product_quick_stock_rule for OpenERP                                      #
#   Copyright (C) 2012 Akretion Sébastien BEAU <sebastien.beau@akretion.com>  #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

from openerp.osv.orm import Model
from openerp.osv import fields


class product_product(Model):
    _inherit = "product.product"

    def _get_min_stock(self, cr, uid, ids, field_name, arg, context=None):
        orderpoint_obj = self.pool.get('stock.warehouse.orderpoint')
        res={}
        for product_id in ids:
            op_ids = orderpoint_obj.search(cr, uid, ['|', ('active', '=', False),
                            ('active', '=', True), ('product_id', '=', product_id)], context=context)
            if op_ids:
                op = orderpoint_obj.browse(cr, uid, op_ids[0], context=context)
                res[product_id] = op.product_min_qty
            else:
                res[product_id] = 0
        return res

    def _set_min_stock(self, cr, uid, product_id, name, value, arg, context=None):
        print 'set stock'
        orderpoint_obj = self.pool.get('stock.warehouse.orderpoint')
        op_ids = orderpoint_obj.search(cr, uid, [('product_id', '=', product_id)], context=context)
        if op_ids:
            orderpoint_obj.write(cr, uid, op_ids[0], {'product_min_qty': value}, context=context)
        elif value:
            vals = self._prepare_orderpoint_minrule(cr, uid, product_id, value, context=context)
            vals['active'] = False
            orderpoint_obj.create(cr, uid, vals, context=context)
        return True

    def _get_rule_status(self, cr, uid, ids, field_name, arg, context=None):
        orderpoint_obj = self.pool.get('stock.warehouse.orderpoint')
        res={}
        for product_id in ids:
            if orderpoint_obj.search(cr, uid, [('product_id', '=', product_id)], context=context):
                res[product_id] = True
            else:
                res[product_id] = False
        return res

    def _prepare_orderpoint_minrule(self, cr, uid, product_id, min_qty=0, context=None):
        orderpoint_obj = self.pool.get('stock.warehouse.orderpoint')
        context['default_product_id'] = product_id
        res = orderpoint_obj.default_get(cr, uid, orderpoint_obj._columns.keys(), context=context)
        res['product_min_qty'] = min_qty
        return res

    def _set_rule_status(self, cr, uid, product_id, name, value, arg, context=None):
        orderpoint_obj = self.pool.get('stock.warehouse.orderpoint')
        op_ids = orderpoint_obj.search(cr, uid, ['|', ('active', '=', False),
                        ('active', '=', True), ('product_id', '=', product_id)], context=context)
        if op_ids:
            orderpoint_obj.write(cr, uid, op_ids[0], {'active': value}, context=context)
        elif value:
            vals = self._prepare_orderpoint_minrule(cr, uid, product_id, context=context)
            orderpoint_obj.create(cr, uid, vals, context=context)
        return True

    _columns = {
        'active_rule': fields.function(_get_rule_status, fnct_inv =_set_rule_status, type='boolean', string='Active Rule'),
        'qty_min': fields.function(_get_min_stock, fnct_inv =_set_min_stock, type='float', string='Minimal Stock'),
        }


class stock_warehouse_orderpoint(Model):
    """
    Defines Minimum stock rules.
    """
    _inherit = "stock.warehouse.orderpoint"
    _columns = {
        'sequence': fields.integer('Sequence', require=True),
        }

    def _get_default_warehouse(self, cr, uid, context=None):
        warehouse_ids = self.pool.get('stock.warehouse').search(cr, uid, [], context=context)
        return warehouse_ids and warehouse_ids[0] or False

    def default_get(self, cr, uid, fields, context=None):
        defaults = super(stock_warehouse_orderpoint, self).default_get(cr, uid, fields, context=context)
        if 'product_uom' in fields and not defaults.get('product_uom') and defaults.get('product_id'):
            prod = self.pool.get('product.product').browse(cr, uid, defaults['product_id'], context=context)
            defaults['product_uom'] = prod.uom_id.id
        if 'warehouse_id' in fields and not defaults.get('location_id') and defaults.get('warehouse_id'):
            w = self.pool.get('stock.warehouse').browse(cr, uid, defaults['warehouse_id'], context=context)
            defaults['location_id'] = w.lot_stock_id.id
        return defaults


    _defaults = {
        'warehouse_id': _get_default_warehouse,
        'product_max_qty': 0,
        'sequence': 0,
        }
