# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Analytic Online, for OpenERP
#    Copyright (C) 2013 XCG Consulting (http://odoo.consulting)
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
    "name": "Analytic Structure",
    "version": "2.0.1",
    "author": "XCG Consulting, Odoo Community Association (OCA)",
    "category": 'Dependency',
    'license': 'AGPL-3',
    "summary": (
        "This module allows to use several analytic dimensions through"
        "a structure related to an object model"
    ),
    'website': 'http://www.openerp-experts.com',
    "depends": [
        'base',
        'base_model_metaclass_mixin',
    ],
    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'analytic_views.xml',
        'analytic_menus.xml',
    ],
    'css': [
        'static/src/css/analytic_structure.css',
    ],
    'installable': True,
}
