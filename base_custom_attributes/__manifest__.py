# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   base_attribute.attributes for OpenERP                                     #
#   Copyright (C) 2011 Akretion Benoît GUILLOT <benoit.guillot@akretion.com>  #
#   Copyright (C) 2013 Akretion Raphaël VALYI <raphael.valyi@akretion.com>    #
#   Copyright (C) 2015 Savoir-faire Linux                                     #
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
    'version': '10.0.0.0.1',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'author': "Akretion,"
    "Odoo Community Association (OCA),"
    "Savoir-faire Linux",
    'website': 'https://github.com/OCA/product-attribute/',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'security/attribute_security.xml',
        'views/menu_view.xml',
        'views/attribute_attribute_view.xml',
        'views/attribute_group_view.xml',
        'views/attribute_option_view.xml',
        'views/attribute_set_view.xml',
        'wizard/attribute_option_wizard_view.xml',
    ],
    'external_dependencies': {
        'python': ['unidecode'],
    }
}
