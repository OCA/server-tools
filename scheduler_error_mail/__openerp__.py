# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Scheduler Error Mail',
    'summary': """
        Allows to send mails to followers of the scheduled action in case
        of errors""",
    'version': '7.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://acsone.eu',
    'depends': ['base', 'mail'],
    'data': ['views/ir_cron_view.xml', ],
    'demo': [
    ],
    'installable': True,
    'application': False,
}
