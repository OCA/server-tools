# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Base Import Deffered Parent Store',
    'summary': """
        Add an options in the base import to allow deffered parent store
        computation""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/server-tools',
    'depends': [
        'base_import'
    ],
    'data': [
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/base_import.xml',
    ],
}
