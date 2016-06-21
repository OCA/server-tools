# -*- coding: utf-8 -*-
{
    'name': "PostgreSQL Trigram Search",
    'summary': """PostgreSQL Trigram Search""",
    'category': 'Uncategorized',
    'version': '8.0.1.0.0',
    'website': 'https://odoo-community.org/',
    'author': 'Daniel Reis, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'views/trgm_index.xml',
    ],
    'installable': True,
}
