# coding: utf-8
# @ 2015 Florian DA COSTA @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Attachment Base Synchronize',
    'version': '10.0.1.0.0',
    'author': 'Akretion,Odoo Community Association (OCA)',
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
    ],
    'demo': [
        'demo/attachment_metadata_demo.xml'
    ],
    'installable': True,
    'application': False,
    'images': [],
}
