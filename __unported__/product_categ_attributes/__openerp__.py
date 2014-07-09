# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   product_custom_attributes for OpenERP                                     #
#   Copyright (C) 2013 Akretion Raphaël Valyi <raphael.valyi@akretion.com>    #
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
    'name': 'product_categ_attributes',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """Makes it possible to inherit product attributes from its categories
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': ['product_custom_attributes', 'product_m2mcategories'],
    'init_xml': [],
    'update_xml': [
        "product_view.xml"
    ],
    'demo_xml': [],
    'installable': False,
    'active': False,
}

