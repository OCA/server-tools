# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Fuzzy Search",
    'summary': "Fuzzy search with the PostgreSQL trigram extension",
    'category': 'Uncategorized',
    'version': '8.0.1.0.0',
    'website': 'https://odoo-community.org/',
    'author': 'bloopark systems GmbH & Co. KG, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'views/trgm_index.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
