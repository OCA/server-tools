# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    product_multi_price for OpenERP                                          #
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


{
    'name': 'product_multi_price',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """empty""",
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com/',
    'depends': ['product','account', 'sale','product_prices_on_variant'],
    'init_xml': [],
    'update_xml': [
           'product_price_fields_view.xml',
           'product_view.xml',
           'product_price_field_config.xml',
           'account_view.xml',
           'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'installable': False,
    'active': False,
}

