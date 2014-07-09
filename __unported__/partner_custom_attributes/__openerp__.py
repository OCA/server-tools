# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#   Author: Leonardo Pistone <leonardo.pistone@camptocamp.com>                #
#   Copyright 2014 Camptocamp SA                                              #
#                                                                             #
#   Inspired by the module product_custom_attributes                          #
#   by Benoît GUILLOT <benoit.guillot@akretion.com>, Akretion                 #
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

{'name': 'Partner Custom Attributes',
 'version': '0.1.0',
 'category': 'Generic Modules/Others',
 'license': 'AGPL-3',
 'description': """
Partner custom attributes
=========================

This module adds the possibility to easily create custom fields on Partners.
Each partner can be linked to an attribute set.  Each attribute has custom
fields.

This module is inspired by the module product_custom_attributes by Benoît
GUILLOT, Akretion

""",
 'complexity': 'normal',
 'author': 'Camptocamp',
 'website': 'http://www.camptocamp.com/',
 'depends': ['base_custom_attributes'],
 'data': ['partner_view.xml',
          'custom_attributes_view.xml',
          'wizard/open_partner_by_attribute_set.xml'
          ],
 'test': ['test/partner_attribute_test.yml'],
 'installable': False,
 'active': False,
 }
