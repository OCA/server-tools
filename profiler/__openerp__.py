# coding: utf-8
# License AGPL-3 or later (http://www.gnu.org/licenses/lgpl).
# Copyright 2014 Anybox <http://anybox.fr>
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>

{
    'name': 'profiler',
    'version': '8.0.1.0.0',
    'category': 'Tools',
    'license': 'AGPL-3',
    'author': 'Anybox, Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://odoo-community.org',
    'depends': ['website'],
    'data': [
        'data/profiler_excluding.xml',
        'security/group.xml',
        'views/profiler.xml',
        'views/assets.xml',
    ],
    'external_dependencies': {
        'python': [
            'pstats_print2list',
        ],
    },
    'qweb': [
        'static/src/xml/player.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_load': 'post_load',
}
