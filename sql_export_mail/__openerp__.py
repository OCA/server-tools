# -*- coding: utf-8 -*-
# Copyright 2017 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'SQL Export Mail',
    'version': '8.0.1.0.0',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Others',
    'summary': 'Export data in csv file with SQL requests',
    'depends': [
        'sql_export',
        'mail',
    ],
    'data': [
        'views/sql_export_view.xml',
        'mail_template.xml',
    ],
    'installable': True,
    }
