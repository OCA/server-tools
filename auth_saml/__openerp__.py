# -*- coding: utf-8 -*-
##############################################################################
#
#    Saml2 Authentication for Odoo
#    Copyright (C) 2010-2016 XCG Consulting <http://odoo.consulting>
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
    'author': 'XCG Consulting, Odoo Community Association (OCA)',
    'maintainer': 'XCG Consulting',
    'website': 'http://odoo.consulting',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'base_setup',
        'web',
        'auth_crypt',
    ],

    'data': [
        'data/auth_saml.xml',
        'data/ir_config_parameter.xml',

        'security/ir.model.access.csv',

        'views/auth_saml.xml',
        'views/base_settings.xml',
        'views/res_users.xml',
    ],
    'installable': True,
    'auto_install': False,
    'external_dependencies': {
        'python': ['lasso'],
    },
}
