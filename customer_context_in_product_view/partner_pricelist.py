# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution - module extension
#    Copyright (C) 2014- O4SB (<http://o4sb.com>).
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
'''This module allows products view to lookup price by customer (as opposed
to default from pricelist)'''

from openerp.osv import orm, fields


class ProductProduct(orm.Model):
    '''
    inherited product.product to add customer field
    and amend search functions
    '''
    _inherit = 'product.product'

    _columns = {
        'customer_context_id': fields.dummy(
                        string='Customer', relation='res.partner',
                        type='many2one', domain=[('customer', '=', True)]),
        }


class ProductPricelist(orm.Model):
    _inherit = 'product.pricelist'

    def name_search(self, cr, user, name='', args=None, operator='ilike',
                    context=None, limit=100):
        if context is None:
            context = {}
        if context.get('pricelist', False) == 'customer_context':
            partner = self.pool['res.partner'].browse(cr, user,
                                                      context['customer_context'])
            pricelist = partner.property_product_pricelist
            context['pricelist'] = pricelist.id
            return [(context['pricelist'], pricelist.name)]
        else:
            return super(ProductPricelist, self).name_search(
                                            cr, user, name=name, args=args,
                                            operator=operator, context=context,
                                            limit=limit)
