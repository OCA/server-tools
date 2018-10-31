# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Keycloak auth integration",
    "summary": "Integrate Keycloak into your SSO",
    "version": "9.0.1.0.0",
    'category': 'Tools',
    "website": "https://github.com/OCA/server-tools",
    'author': 'Camptocamp, Odoo Community Association (OCA)',
    "license": "AGPL-3",
    "depends": [
        "auth_oauth",
    ],
    "data": [
        'data/auth_oauth_provider.xml',
        'wizard/keycloak_sync_wiz.xml',
        'wizard/keycloak_create_wiz.xml',
        'views/auth_oauth_views.xml',
        'views/res_users_views.xml',
    ],
    "installable": True,
}
