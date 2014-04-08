# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    product_brand for OpenERP                                                  #
#    Copyright (C) 2009 NetAndCo (<http://www.netandco.net>).                   #
#    Authors, Mathieu Lemercier, mathieu@netandco.net,                          #
#             Franck Bret, franck@netandco.net                                  #
#    Copyright (C) 2011 Akretion Benoît Guillot <benoit.guillot@akretion.com>   #
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
from openerp.osv import orm, fields


class product_brand(orm.Model):
    _name = 'product.brand'
    _columns = {
        'name': fields.char('Brand Name'),
        'description': fields.text('Description', translate=True),
        'partner_id': fields.many2one(
            'res.partner',
            'partner',
            help='Select a partner for this brand if it exists.',
            ondelete='restrict'),
        'logo': fields.binary('Logo File')
    }


class product_template(orm.Model):
    _inherit = 'product.template'
    _columns = {
        'product_brand_id': fields.many2one(
            'product.brand',
            'Brand',
            help='Select a brand for this product.',
            ondelete='restrict')
    }
