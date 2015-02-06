# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    "name" : "Product Information Import from icecat",
    "version" : "1.0",
    "author" : "Zikzakmedia",
    "website" : "http://www.zikzakmedia.com",
    "license": "AGPL-3",
    "category" : "Added functionality",
    "depends" : ["base","product","product_images_olbs"],
    "init_xml" : [],
    "demo_xml" : [],
    "description": """
    Import information XML from icecat to OpenERP products.
    This wizard download XML in openerp-server (addons/product_icecat/xml) and after process data mapping line to product import.
    - Language import: User preference or force into wizard (option)
    - HTML Category option: create list details
    - FTP image
    http://www.icecat.biz/
    """,
    'update_xml': [
        'security/ir.model.access.csv',
        'product_icecat.xml',
        'wizard/wizard_product_icecat.xml',
    ],
    'test':[''],
    'installable': False,
    'active': False,
}
