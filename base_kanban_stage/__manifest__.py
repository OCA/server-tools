# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Kanban - Stage Support',
    'summary': 'Provides stage model and abstract logic for inheritance',
    'version': '12.0.1.2.2',
    'author': 'LasLabs, Odoo Community Association (OCA)',
    'category': 'base',
    'depends': [
        'base',
    ],
    'website': 'https://github.com/OCA/server-tools',
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/base_kanban_abstract.xml',
        'views/base_kanban_stage.xml',
        'views/ir_model_views.xml',
    ],
    'installable': True,
    'application': False,
}
