# Copyright (c) 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Remote Base",
    'version': '11.0.1.0.2',
    'category': 'Generic Modules/Base',
    'author': "Creu Blanca, Odoo Community Association (OCA)",
    'website': 'http://github.com/OCA/server-tools',
    'license': 'AGPL-3',
    "depends": ['web', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_remote_views.xml',
    ],
    'installable': True,
    'application': True,
}
