# -*- coding: utf-8 -*-
{
    'name': "Ldap multi login",

    'summary': """
        The module allows you to specify several fields in ldap to find the entered login""",

    'description': """
        The module allows you to specify several fields in ldap to find the entered login.
        Also you can specify which ldap field to use as the login when creating the user Odoo.
    """,
    'author': "RYDLAB",
    'category': 'Tools',
    'version': '1.0',
    'depends': ['base', 'auth_ldap'],
    'data': [
        'views/users_ldap_view.xml',
    ],
}
