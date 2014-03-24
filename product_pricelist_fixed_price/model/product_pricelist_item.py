# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com> 
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.tools.translate import _


class product_pricelist_item(orm.Model):
    _inherit = 'product.pricelist.item'

    def _price_field_get_ext(self, cr, uid, context=None):
        result = super(product_pricelist_item, self)._price_field_get(
                                    cr, uid, context=context)
        result.append((-3, _('Fixed Price')))
        return result

    _columns = {
        'base_ext': fields.selection(_price_field_get_ext, 'Based on',
                                     required=True, size=-1,
                                     help="Base price for computation."),
    }
    _defaults = {
        'base_ext': -1,
    }

    def onchange_base_ext(self, cr, uid, ids, base_ext, context=None):
        if base_ext == -3:
            # Simulate be based on first found price that allows the trick
            return {
                'value': {'base': 1,
                          'price_discount': -1,}
            }
        return {'value': {'base': base_ext}}
