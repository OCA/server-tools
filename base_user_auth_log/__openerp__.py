# -*- coding: utf-8 -*-
# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Users authentification logs',
    'version': '8.0.1.0.0',
    'category': 'Tools',
    'license': 'AGPL-3',
    'summary': 'Adds users authentication logs',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_users_auth_log.xml',
        'views/res_users.xml',
    ],
    'installable': True,
}
