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



{
    'name': 'product_prices_on_variant',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """
    This module move the field price from the template to the variant.
    This module is needed by product_multi_price. Be careful when using this module.
    As this change the original behaviour of OpenERP when using variant.
    """,
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com/',
    'depends': [
        'product',
        ],
    'init_xml': [],
    'update_xml': [
    ],
    'demo_xml': [],
    'installable': False,
    'active': False,
}

