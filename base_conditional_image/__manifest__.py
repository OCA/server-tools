# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    'name': 'Conditional Images',
    'version': '12.0.1.0.1',
    'author': 'Camptocamp, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'category': 'Misc',
    'depends': [
        'base',
    ],
    'website': 'http://github.com/OCA/server-tools',
    'data': [
        'views/image_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
