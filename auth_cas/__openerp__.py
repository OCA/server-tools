# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
    'name': 'Auth CAS',
    'version': '0.1',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'category': 'Generic Modules',
    'summary': 'Auth CAS',
    'description': """
Auth CAS
========

This module allows Odoo to authenticate via a CAS v[12] server.

Contributors
------------
* Joao Alfredo Gama Batista (joao.gama@savoirfairelinux.com)
""",
    'depends': [
        'web',
    ],
    'external_dependencies': {
        'python': ['requests', 'lxml'],
    },
    'data': ['views/auth_cas_login.xml'],
    'qweb': ['static/src/xml/base.xml'],
    'installable': True,
    'application': False,
}
