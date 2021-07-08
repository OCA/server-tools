# Copyright 2016-2017 Versada <https://versada.eu/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Sentry',
    'summary': 'Report Odoo errors to Sentry',
    'version': '12.0.2.0.0',
    'category': 'Extra Tools',
    'website': 'https://odoo-community.org/',
    'author': 'Mohammed Barsi,'
              'Versada,'
              'Nicolas JEUDY,'
              'Odoo Community Association (OCA),'
              'Vauxoo',
    'maintainers': ['barsi', 'naglis', 'versada', 'moylop260', 'fernandahf'],
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [
            'sentry_sdk',
        ]
    },
    'depends': [
        'base',
    ],
    'post_load': 'post_load',
}
