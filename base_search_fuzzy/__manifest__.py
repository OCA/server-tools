# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Fuzzy Search",
    'summary': "Fuzzy search with the PostgreSQL trigram extension",
    'category': 'Uncategorized',
    'version': '10.0.1.1.0',
    'website': 'https://github.com/OCA/server-tools'
               '/tree/10.0/base_search_fuzzy',
    'author': 'bloopark systems GmbH & Co. KG, '
              'Eficent, '
              'Serpent CS, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': ['base'],
    'data': [
        'views/trgm_index.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
