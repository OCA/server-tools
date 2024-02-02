# -*- coding: utf-8 -*-
# Copyright 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2016 ACSONE SA/NA (<http://acsone.eu>)

{
    'name': "Optional quick create",
    'version': '10.0.1.0.1',
    'category': 'Tools',
    'summary': "Avoid 'quick create' on m2o fields, on a 'by model' basis",
    'author': "Agile Business Group,Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/server-tools'
               '/tree/10.0/base_optional_quick_create',
    'license': 'AGPL-3',
    "depends": ['base'],
    "data": [
        'views/model_view.xml',
    ],
    'installable': True,
}
