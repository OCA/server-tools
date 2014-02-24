# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com> 
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

{
    "name": "Fixed price in pricelists",
    "version": "2.0",
    "author": "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "category": "Sales Management",
    "description": """
Fixed price on pricelist rule
=============================

Adds a new option on pricelist rules to set a fixed price. This is made using
a trick that writes on the back 100% in the discount to the base price to get
a zero base that will add only the price we put in the surcharge price.
    """,
    "website": "www.serviciosbaeza.com",
    "license": "AGPL-3",
    "depends": [
        "product",
    ],
    "demo": [],
    "data": [
        'view/product_pricelist_item_view.xml',
    ],
    "installable": True,
    "active": False,
}
