# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: el_rodo_1 (rodo@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
    "name": "Products Customer Code",
    "version": "1.0",
    "author": "Vauxoo,Odoo Community Association (OCA)",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "category": "Generic Modules/Product",
    "summary": "Add many Customers' Codes in product",
    "depends": [
            "base",
            "product",
    ],
    "description": """
Customer' codes in product
==========================

This module does just like the product.supplierinfo but for customers instead. For instance it
allows to have different references for the same product according to the customer.

.. image:: product_customer_code/static/src/img/screenshot1.png

.. tip::

    You will need install some of the Apps which enable the product menu to see this module in
    action, like Sales, Purchase or Warehouse Management
     """,
    "data": [
        "security/product_customer_code_security.xml",
        "security/ir.model.access.csv",
        "product_customer_code_view.xml",
        "product_product_view.xml",
    ],
    "active": False,
    'installable': False,
}
