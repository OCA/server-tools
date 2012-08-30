# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   product_prices_on_variant for OpenERP                                          #
#   Copyright (C) 2011 Akretion Benoît GUILLOT <benoit.guillot@akretion.com>  #
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
import decimal_precision as dp


class product_product(Model):
    _inherit = "product.product"
    _columns = {
        'list_price': fields.float('Sale Price',
                                   digits_compute=dp.get_precision('Sale Price'),
                                   help="Base price for computing the customer price. "
                                   "Sometimes called the catalog price."),
        'standard_price': fields.float('Cost Price', required=True,
                                       digits_compute=dp.get_precision('Purchase Price'),
                                       help="Product's cost for accounting stock valuation. "
                                       "It is the base price for the supplier price."),
        }
    _defaults = {
        'list_price': lambda *a: 1,
        'standard_price': lambda *a: 1,
        }


