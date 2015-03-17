# -*- coding: utf-8 -*-
##############################################################################
#
#    Saml2 Authentication for Odoo
#    Copyright (C) 2010-2015 XCG Consulting <http://odoo.consulting>
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
    'name': 'Saml2 Authentication',
    'version': '3.0',
    'category': 'Tools',
    'description': """
Allow users to login through Saml2 Provider.
===================================
""",
    'author': 'XCG Consulting s.a.s.',
    'maintainer': 'XCG Consulting s.a.s.',
    'website': 'http://www.xcg-consulting.fr',
    'depends': ['base', 'web', 'base_setup'],

    'data': [
        'data/auth_saml.xml',
        'data/ir_config_parameter.xml',

        'security/ir.model.access.csv',

        'views/auth_saml.xml',
        'views/base_settings.xml',
        'views/res_users.xml',
    ],

    'js': ['static/src/js/auth_saml.js'],
    'css': [
        'static/lib/zocial/css/zocial.css',
        'static/src/css/auth_saml.css',
    ],
    'qweb': ['static/src/xml/auth_saml.xml'],
    'installable': True,
    'auto_install': False,
}
