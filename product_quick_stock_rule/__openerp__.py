# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   product_quick_stock_rule for OpenERP                                      #
#   Copyright (C) 2012 Akretion Sébastien BEAU <sebastien.beau@akretion.com>  #
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
    'name': 'product_quick_stock_rule',
    'version': '0.1',
    'category': 'Stock',
    'license': 'AGPL-3',
    'description': """
        This module simplifies the stock rule managment.
        Two fields have been added on product view : 'active_rule' and 'min_qty'
        If you click on 'active rule' and select a 'min_qty' a stock rule will be automatically
        generated.
        If you unselect the 'active rule' the rule will be deactivated 
        and the field min_qty will be read only.
        """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': ['procurement'],
    'init_xml': [],
    'update_xml': [
           'product_view.xml',
    ],
    'demo_xml': [],
    'installable': False,
    'active': False,
}

