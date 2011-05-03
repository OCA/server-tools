# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    product_is_a_gift for OpenERP                                              #
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>   #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################

from osv import osv, fields
import netsvc


class stock_picking(osv.osv):
    _inherit = "stock.picking"

    _columns = {
        'gift_message': fields.text('Gift Message'),
    }

    def create(self, cr, uid, vals, context=None):
        print 'create picking', vals.get('sale_id', False) and not 'gift_message' in vals
        if vals.get('sale_id', False) and not 'gift_message' in vals:
            order = self.pool.get('sale.order').browse(cr, uid, vals['sale_id'], context=context)
            print 'order.name', order.name, order.gift_message
            vals.update({'gift_message' : order.gift_message})
            print 'vals', vals
        return super(stock_picking, self).create(cr, uid, vals, context=context)

stock_picking()


class stock_move(osv.osv):
    _inherit = "stock.move"

    _columns = {
        'gift_message': fields.text('Gift Message'),
        'need_gift_wrap': fields.boolean('Need Gift Wrap'),
    }

    def create(self, cr, uid, vals, context=None):
        print 'create move', vals.get('sale_line_id', False) and not ('gift_message' in vals and 'need_gift_wrap' in vals)
        if vals.get('sale_line_id', False) and not ('gift_message' in vals and 'need_gift_wrap' in vals):
            line = self.pool.get('sale.order.line').browse(cr, uid, vals['sale_line_id'], context=context)
            vals.update({'gift_message' : line.gift_message, 'need_gift_wrap': line.need_gift_wrap})
            print 'vals', vals
        return super(stock_move, self).create(cr, uid, vals, context=context)


stock_move()
