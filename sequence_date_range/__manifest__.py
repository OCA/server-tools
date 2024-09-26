# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "sequence_date_range",
    'summary': """Module used to use the year of the date_to
    into sequences (instead of date_from)""",
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': "https://github.com/OCA/server-tools"
               "/tree/10.0/sequence_date_range",
    'category': 'account',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'demo': [
        'demo/ir_sequence.xml',
    ],
    'data': [
        'views/ir_sequence.xml',
    ],
}
