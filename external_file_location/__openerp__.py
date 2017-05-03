# coding: utf-8
# @ 2016 florian DA COSTA @ Akretion
# © 2016 @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'External File Location',
    'version': '9.0.1.0.0',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com/',
    'license': 'AGPL-3',
    'category': 'Generic Modules',
    'depends': [
        'attachment_base_synchronize',
    ],
    'external_dependencies': {
        'python': [
            'fs',
            'paramiko',
        ],
    },
    'data': [
        'views/menu.xml',
        'views/attachment_view.xml',
        'views/location_view.xml',
        'views/task_view.xml',
        'data/cron.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/task_demo.xml',
    ],
    'installable': True,
    'application': False,
}
