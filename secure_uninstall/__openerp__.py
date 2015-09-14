# coding: utf-8
##############################################################################
#
#    Copyright (C) All Rights Reserved 2014 Akretion
#    @author David BEAL <david.beal@akretion.com>
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
###############################################################################

{
    'name': 'Secure Uninstall',
    'version': '0.1',
    'author': "Akretion,Odoo Community Association (OCA)",
    'maintener': 'Akretion',
    'category': 'Base',
    'summary': "Ask password to authorize uninstall",
    'depends': [
        'base',
    ],
    'description': """
Secure Uninstall
================

Ask Master Password ('admin_passwd' key from config file)
before to proceed to module uninstallation


Contributors
------------
* David BEAL <david.beal@akretion.com>

""",
    'data': ['wizard_view.xml'],
    'website': 'http://www.akretion.com/',
    'license': 'AGPL-3',
    'tests': [],
    'installable': True,
}
