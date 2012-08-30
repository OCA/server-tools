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

from openerp.osv.orm import Model
from openerp.osv import fields


class stock_picking(Model):
    _inherit = "stock.picking"
    _columns = {
        'gift_message': fields.text('Gift Message'),
        }


class stock_move(Model):
    _inherit = "stock.move"
    _columns = {
        'gift_message': fields.text('Gift Message'),
        'need_gift_wrap': fields.boolean('Need Gift Wrap'),
        }

    def _prepare_chained_picking(self, cr, uid, pick_name, picking, ptype, move, context=None):
        res = super(stock_move, self)._prepare_chained_picking(cr, uid, pick_name, picking, ptype, move, context=context)
        res['gift_message'] = picking.gift_message
        return res
