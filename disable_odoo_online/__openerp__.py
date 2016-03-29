# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
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
    "name": "Remove odoo.com bindings",
    "version": "9.0.0.1.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "complexity": "normal",
    "description": """
This module deactivates all bindings to openerp.com that
come with the standard code:

* update notifier code is deactivated and the function is overwritten
* apps and updates menu items in settings are hidden inside Tools\\Parameters
* help and account menu items in user menu are removed
* prevent lookup of OPW for current database uuid and resulting
  'unsupported' warning
    """,
    "category": "",
    "depends": [
        'base',
        'mail',
    ],
    "data": [
        "views/disable_openerp_online.xml",
        'views/ir_ui_menu.xml',
        'data/ir_cron.xml',
    ],
    "qweb": [
        'static/src/xml/base.xml',
    ],
    'installable': True,
}
