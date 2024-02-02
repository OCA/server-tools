# -*- coding: utf-8 -*-
# © Daniel Reis (https://launchpad.com/~dreis-pt)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).
{
    'name': "LDAP mapping for user name and e-mail",
    'version': "10.0.1.0.0",
    'depends': ["auth_ldap"],
    'author': "Daniel Reis (https://launchpad.com/~dreis-pt),"
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools"
               "/tree/10.0/users_ldap_mail",
    'license': 'AGPL-3',
    'category': "Tools",
    'data': [
        'views/users_ldap_view.xml',
    ],
    'installable': True,
}
