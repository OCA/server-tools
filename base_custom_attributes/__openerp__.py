# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   base_custom_attributes for OpenERP                                        #
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
    'name': 'base_custom_attributes',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """This module adds the possibility to easily create custom attributes in any OpenERP business object. See the product_custom_attributes module for instance.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': ['base'],
    'init_xml': [],
    'update_xml': [
           'security/ir.model.access.csv',
           'security/attribute_security.xml',
           'custom_attributes_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'external_dependencies' : {
        'python' : ['unidecode'],
    }

}

