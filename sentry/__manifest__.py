# Copyright 2016-2017 Versada <https://versada.eu/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Sentry',
    'summary': 'Report Odoo errors to Sentry',
    'version': '11.0.1.0.0',
    'category': 'Extra Tools',
    'website': 'https://odoo-community.org/',
    'author': 'Mohammed Barsi,'
              'Versada,'
              'Nicolas JEUDY,'
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [
            'raven',
        ]
    },
    'depends': [
        'base',
    ],
}
