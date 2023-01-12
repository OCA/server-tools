# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'SQL Request Abstract',
    'version': '10.0.1.0.1',
    'author': 'GRAP,Akretion,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/server-tools'
               '/tree/10.0/sql_request_abstract',
    'license': 'AGPL-3',
    'category': 'Tools',
    'summary': 'Abstract Model to manage SQL Requests',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir_module_category.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
