# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Fuzzy Search",
    'summary': "Fuzzy search with the PostgreSQL trigram extension",
    'category': 'Uncategorized',
    'version': '11.0.1.0.0',
    'website': 'https://odoo-community.org/',
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
