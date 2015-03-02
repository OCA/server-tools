# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################
{
    "name" : "Supplier unit price",
    "version" : "0.1",
    "author" : "Savoir-faire Linux,Odoo Community Association (OCA)",
    "website" : "http://www.savoirfairelinux.com",
    "license" : "GPL-3",
    "category" : "Product",
    "complexity" : "easy",
    "description": """
	On the product form, in the suppliers tab, you have to click on the 
        line to get the prices of the product from that supplier.

        This module displays the unit price directly on the product form by
        adding a function field to store the unit price to the supplierinfo
        object and adding it to its tree view.
    """,
    "depends" : ['product'],
    "init_xml" : [],
    "update_xml" : [
        'supplierinfo_view.xml'
    ],
    "demo_xml" : [],
    "installable" : True,
    "certificate" : ''
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

