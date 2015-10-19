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
SAML2 authentication
====================

Let users log into Odoo via an SAML2 provider.

This module allows to deport the management of users and passwords in an
external authentication system to provide SSO functionality (Single Sign On)
between Odoo and other applications of your ecosystem.


WARNING: this module requires auth_crypt. This is because you still have the
    option if not recommended to allow users to have a password stored in odoo
    at the same time as having a SALM provider and id.


Benefits
--------

* Reducing the time spent typing different passwords for different accounts.

* Reducing the time spent in IT support for password oversights.

* Centralizing authentication systems.

* Securing all input levels / exit / access to multiple systems without
  prompting users.

* The centralization of access control information for compliance testing to
  different standards.


Dependencies
------------

This addon requires `lasso`_.

.. _lasso: http://lasso.entrouvert.org
""",
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
