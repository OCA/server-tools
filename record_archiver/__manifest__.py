# Copyright 2015 Yannick Vaucher (Camptocamp SA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Records Archiver',
    'version': '11.0.1.0.0',
    'author': 'Camptocamp, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'category': 'misc',
    'depends': ['base'],
    'website': 'https://github.com/OCA/server-tools',
    'data': [
        'security/ir.model.access.csv',
        'views/record_lifespan_view.xml',
        'data/cron.xml',
    ],
}
