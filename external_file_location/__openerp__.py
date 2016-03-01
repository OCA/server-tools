# coding: utf-8
# @ 2015 Valentin CHEMIERE @ Akretion
# © 2016 @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'external_file_location',
    'version': '8.0.1.0.0',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'www.akretion.com',
    'license': 'AGPL-3',
    'category': 'Generic Modules',
    'depends': [
        'attachment_metadata',
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
    'installable': True,
    'application': False,
    'images': [],
}
