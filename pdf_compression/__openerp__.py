# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "PDF Compression",
    'summary': """compresses the pdf files for ir.attachement""",
    'author':
        "Benjamin Bachmann ,"
        "bloopark systems GmbH & Co. KG ,"
        "Odoo Community Association (OCA)",
    'website': "http://www.bloopark.de",
    'category': 'attachement',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'report',
        'knowledge',
    ],
    'data': [
        'views/backend.xml',
        'data/ir_values.xml',
    ],
    'installable': True,
    'auto_install': False,
}
