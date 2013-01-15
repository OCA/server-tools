# -*- coding: utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
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

import logging
from openerp.osv import fields, osv
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class product_product(osv.osv):
    _inherit = "product.product"

    def update_weight(self, cr, uid, ids, default=None, context=None):
        mrp_bom = self.pool.get("mrp.bom")
        product_uom_categ = self.pool.get("product.uom.categ")

        for p in self.browse(cr, uid, ids, context=context):
            weight_net = 0.0
            bom_ids = mrp_bom.search(cr, uid,
                                     [('bom_id', '=', p.bom_ids[0].id)])
            for bom in mrp_bom.browse(cr, uid, bom_ids, context=context):
                _logger.warning(mrp_bom.browse(
                    cr, uid, p.bom_ids[0].id, context=context).product_qty)
                if bom.product_uom.category_id.name == 'Weight':
                    weight_net += bom.product_qty
                else:
                    weight_net += (bom.product_qty * bom.product_id.weight_net)

            weight_net = weight_net / mrp_bom.browse(
                cr, uid, p.bom_ids[0].id, context=context).product_qty
            self.write(cr, uid, p.id,
                       {'weight_net': weight_net},
                       context=context)
        return {}
