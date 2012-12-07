# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    product_is_a_gift for OpenERP                                              #
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>   #
#    Copyright (C) 2011 Camptocamp SA. (author Guewen Baconnier)
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

from openerp.osv.orm import Model
from openerp.osv import fields


class sale_order(Model):
    _inherit = "sale.order"
    _columns = {
        'gift_message': fields.text('Gift Message'),
        }

    def _prepare_order_picking(self, cr, uid, order, *args, **kwargs):
        values = super(sale_order, self)._prepare_order_picking(cr, uid, order, *args, **kwargs)
        values.update({'gift_message' : order.gift_message})
        return values


class sale_order_line(Model):
    _inherit = "sale.order.line"
    _columns = {
        'gift_message': fields.text('Gift Message'),
        'need_gift_wrap': fields.boolean('Add Gift Wrap'),
        }

    def _prepare_order_line_move(self, cr, uid, order, line, picking_id, date_planned, *args, **kwargs):
        values = super(sale_order_line, self)._prepare_order_line_move(cr, uid, order, line, picking_id, date_planned, *args, **kwargs)
        values.update({'gift_message': line.gift_message,
                       'need_gift_wrap': line.need_gift_wrap})
        return values
