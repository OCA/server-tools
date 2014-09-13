# -*- coding: utf-8 -*-
##############################################################################
#
#    BizzAppDev
#    Copyright (C) 2004-TODAY bizzappdev(<http://www.bizzappdev.com>).
#    @author Ruchir Shukla <ruchir@bizzappdev.com>
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
    'name': 'OpenERP - Develop - Test Mode',
    'version': '7.0.0',
    "author": "Bizzappdev",
    "website": "http://bizzappdev.com",
    "category": "GenericModules",
    'sequence': 20,
    'summary': 'OpenERP - Develop Test Mode',
    'description': """
OpenERP - Develop - Test Mode
=====================

OpenERP / Odoo Module which help you to set the database for Test or
Development mode.

Features:
---------

    * Set-up Test or Development environment at the level of database.
    * Provides unique mode-bar for notifying either database is in Develop
mode or Test mode.
    * Mail restriction for outgoing mails.


    """,
    'images': [],
    'depends': ["web", "mail"],
    'data': [
        "res_config_view.xml",
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': True,
    'application': False,
    'js': ["static/src/js/mode.js"],
    'qweb': [
        'static/src/xml/mode.xml',
    ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
