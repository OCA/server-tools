# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Analytic Online, for OpenERP
#    Copyright (C) 2013 XCG Consulting (www.xcg-consulting.fr)
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
    "name" : "Analytic Structure",
    "version" : "1.5.2",
    "author" : "XCG Consulting",
    "category": 'Dependency',
    "description": """
This module allows to use several analytic dimensions through a structure
related to an object model.
=========================================================================
    """,
    'website': 'http://www.openerp-experts.com',
    "depends": [
        'base',
        'oemetasl',
    ],
    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'analytic_views.xml',
        'analytic_menus.xml',
    ],
    # 'demo_xml': [],
    'css': [
        'static/src/css/analytic_structure.css',
    ],
    'test': [],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
