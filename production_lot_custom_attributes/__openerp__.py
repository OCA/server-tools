# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#   Author: Leonardo Pistone <leonardo.pistone@camptocamp.com>                #
#   Copyright 2013 Camptocamp SA                                              #
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

{'name': 'production_lot_custom_attributes',
 'version': '0.1.1',
 'category': 'Generic Modules/Others',
 'license': 'AGPL-3',
 'description': """
Production lot custom attributes
================================

This module adds the possibility to easily create custom fields on stock
production lots. Each lot can be linked to an attribute set.
Each attribute has custom fields (for example, you don't need the same field
for a fridge and a camera).
In particular it's used by the Magento Magentoerpconnect module to match the
EAV flexibility of Magento.
This module is inspired by the module product_custom_attributes by
Benoît GUILLOT, Akretion

 """,
 'complexity': 'normal',
 'author': 'Camptocamp',
 'website': 'http://www.camptocamp.com/',
 'depends': ['stock', 'base_custom_attributes'],
 'data': ['lot_view.xml',
          'custom_attributes_view.xml',
          'wizard/open_lot_by_attribute_set.xml'
          ],
 'test': [
     'test/lot_attribute_test.yml',
 ],
 'installable': True,
 'active': False,
 }
