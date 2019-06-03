# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Database Auto-Backup Download',
    'summary': 'Download the backup files of your database',
    'author': 'Onestein, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/server-tools',
    'category': 'Tools',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'base_setup',
        'base_directory_file_download',
        'auto_backup',
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/backup_directory.xml',
        'views/ir_filesystem_directory.xml',
    ],
    'installable': True,
}
