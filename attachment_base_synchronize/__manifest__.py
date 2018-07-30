# Copyright 2015 Florian DA COSTA @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Attachment Base Synchronize',
    'version': '11.0.1.0.0',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'summary': 'This module enhances ir.attachment for better '
               'control of import and export of files',
    'website': 'https://www.akretion.com',
    'license': 'AGPL-3',
    'category': 'Generic Modules',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'views/attachment_view.xml',
        'security/ir.model.access.csv',
        'data/cron.xml',
        'data/ir_config_parameter.xml',
    ],
    'demo': [
        'demo/attachment_metadata_demo.xml'
    ],
    'installable': True,
    'application': False,
    'images': [],
}
