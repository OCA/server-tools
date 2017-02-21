# coding: utf-8
# Copyright 2015 Anubía, soluciones en la nube,SL (http://www.anubia.es)
#                Alejandro Santana <alejandrosantana@anubia.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Optional CSV import',
    'version': '8.0.1.0.0',
    'category': 'Server tools',
    'summary': 'Group-based permissions for importing CSV files',
    'license': 'AGPL-3',
    'author': 'Odoo Community Association (OCA), '
              'Alejandro Santana <alejandrosantana@anubia.es>',
    'maintainer': 'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/server-tools',
    'depends': [
        'base_import'
    ],
    'data': [
        'security/res_groups.xml',
        'views/base_import.xml',
    ],
    'js': [
        'static/src/js/import.js',
    ],
    'qweb': [
        'static/src/xml/base_import_security_group.xml',
    ],
    'installable': True,
    'post_load': 'post_load',
}
