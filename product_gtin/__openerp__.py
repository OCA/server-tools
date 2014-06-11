# -*- coding: utf-8 -*-
##############################################################################
#
#    Product GTIN module for OpenERP
#    Copyright (C) 2004-2011 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2011 Camptocamp Austria (<http://www.camptocamp.at>)
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
    "name": "Product GTIN EAN8 EAN13 UPC JPC Support",
    "version": "1.1",
    "author":  "ChriCar Beteiligungs- und Beratungs- GmbH",
    "website": "http://www.chricar.at/ChriCar",
    "category": "Sales Management",
    "depends": ["product"],
    "description": """
Product GTIN module
===================

Replaces the EAN13 field on products, partners and packaging by a field with the same technical name that accepts EAN13, EAN8, JPC, UPC and GTIN.
    """,
    "demo": [],
    "data": [],
    "installable": True,
}
