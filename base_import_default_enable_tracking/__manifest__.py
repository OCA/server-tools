# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Base Import Default Enable Tracking',
    'summary': """
        This modules simply enables history tracking when doing an import.""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/server-tools'
               '/tree/10.0/base_import_default_enable_tracking',
    'depends': [
        'base_import',
    ],
    'qweb': [
        'static/src/xml/base_import.xml',
    ],
}
