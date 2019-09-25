# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Directory Files Download',
    'summary': 'Download all files of a directory on server',
    'author': 'Onestein, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/server-tools',
    'category': 'Tools',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'base_setup',
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/ir_filesystem_directory.xml',
    ],
    'installable': True,
}
