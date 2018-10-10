# -*- coding: utf-8 -*-
# Copyright 2016 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Improved Name Search',
    'summary': 'Friendlier search when typing in relation fields',
    'version': '8.0.1.2.0',
    'category': 'Uncategorized',
    'website': 'https://odoo-community.org/',
    'author': 'Daniel Reis, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'data': [
        'views/ir_model.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'depends': [
        'base',
    ],
}
