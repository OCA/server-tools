# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    'name': 'Base Basic Employee Group',
    'version': '11.0.1.0.0',
    'summary': "Adds a basic group in Employee's category",
    'author': 'Eficent,'
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/server-tools',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/webclient_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
