# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Kanban - Stage Support',
    'summary': 'Provides stage model and abstract logic for inheritance',
    'version': '10.0.1.2.1',
    'author': 'LasLabs, Odoo Community Association (OCA)',
    'category': 'base',
    'depends': [
        'base',
    ],
    'website': 'https://github.com/OCA/server-tools'
               '/tree/10.0/base_kanban_stage',
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/base_kanban_abstract.xml',
        'views/base_kanban_stage.xml',
    ],
    'installable': True,
    'application': False,
}
