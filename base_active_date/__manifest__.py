# -*- coding: utf-8 -*-
# Copyright 2017-2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Active Date',
    'version': '10.0.1.0.0',
    'category': 'Generic Modules',
    'summary': 'This module provides an active field, based on current date',
    'author': 'Therp BV'
            ', Odoo Community Association (OCA)',
    'website': 'https://github.com/oca/server-tools',
    'depends': ['base'],
    'license': 'AGPL-3',
    'data': [
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
