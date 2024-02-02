# -*- coding: utf-8 -*-
# Copyright (C) 2015 Akretion (<http://www.akretion.com>)
# @author: Florian da Costa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'SQL Export',
    'version': '10.0.1.0.0',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/server-tools'
               '/tree/10.0/sql_export',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Others',
    'summary': 'Export data in csv file with SQL requests',
    'depends': [
        'sql_request_abstract',
    ],
    'data': [
        'views/sql_export_view.xml',
        'wizard/wizard_file_view.xml',
        'security/sql_export_security.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/sql_export.xml',
    ],
    'installable': True,
    }
