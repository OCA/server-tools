# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'OAuth Provider - JWT',
    'summary': 'Adds the JSON Web Token support for OAuth2 provider',
    'version': '10.0.1.0.0',
    'category': 'Authentication',
    'website': 'http://www.syleam.fr/',
    'author': 'SYLEAM, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'external_dependencies': {
        'python': [
            'jwt',
            'cryptography',
        ],
    },
    'depends': [
        'oauth_provider',
    ],
    'data': [
        'views/oauth_provider_client.xml',
    ],
}
