# -*- coding: utf-8 -*-
# Copyright 2012-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Mail configuration with server_environment',
    'version': '10.0.1.0.0',
    'category': 'Tools',
    'summary': 'Configure mail servers with server_environment_files',
    'author': "Camptocamp,Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'website': 'http://odoo-community.org',
    'depends': ['fetchmail',
                'server_environment',
                ],
    'data': ['views/fetchmail_server_views.xml',
             ],
    'installable': True,
}
