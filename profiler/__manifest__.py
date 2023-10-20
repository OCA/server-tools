# -*- coding: utf-8 -*-
{
    'name': "profiler",
    'author': "Vauxoo, Sunflower IT, Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/server-tools/tree/12.0/profiler",
    'category': 'Tests',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'depends': ["document", "web_tour"],
    'data': [
        'security/ir.model.access.csv',
        'views/profiler_profile_view.xml',
        'views/assets.xml',
    ],
    'post_load': 'post_load',
    'installable': True,
}
