# -*- coding: utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
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

import logging
from openerp.osv import fields, osv
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class product_weight_update(osv.osv_memory):
    _name = "product.weight.update"
    _description = "Update Product Weight"
    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
        'bom_id': fields.many2one('mrp.bom', 'BoM', domain="[('product_id', '=', product_id)]"),
    }

    def default_get(self, cr, uid, fields, context):
        """ To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        product_id = context and context.get('active_id', False) or False
        res = super(product_weight_update, self).default_get(cr, uid, fields, context=context)

        bom_id = self.pool.get('mrp.bom').search(
            cr, uid, [('product_id', '=', product_id)])[0]

        if 'product_id' in fields:
            res.update({'product_id': product_id})

        res.update({'bom_id': bom_id})

        return res

    def update_weight(self, cr, uid, ids, context=None):
        mrp_bom = self.pool.get("mrp.bom")
        product_uom_categ = self.pool.get("product.uom.categ")
        product_product = self.pool.get("product.product")

        if context is None:
            context = {}

        rec_id = context and context.get('active_id', False)
        assert rec_id, _('Active ID is not set in Context')

        for i in self.browse(cr, uid, ids, context=context):
            weight_net = 0.0
            bom_ids = mrp_bom.search(cr, uid,
                                     [('bom_id', '=', i.bom_id.id)])
            for bom in mrp_bom.browse(cr, uid, bom_ids, context=context):
                _logger.warning(_('Weight'))
                if bom.product_uom.category_id.id == 2:
                    weight_net += bom.product_qty
                else:
                    weight_net += (bom.product_qty * bom.product_id.weight_net)

                _logger.warning("%s (%s): %0.2f" % (
                    bom.product_id.name,
                    bom.product_uom.category_id.name, weight_net))
            weight_net = weight_net / mrp_bom.browse(
                cr, uid, i.bom_id.id, context=context).product_qty
            product_product.write(cr, uid, rec_id,
                       {'weight_net': weight_net},
                       context=context)
        return {}

product_weight_update()
