# coding: utf-8
# @ 2015 Valentin CHEMIERE @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'external_file_location',
    'version': '0.0.1',
    'author': 'Akretion',
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
        'menu.xml',
        'attachment_view.xml',
        'location_view.xml',
        'task_view.xml',
        'cron.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    }
