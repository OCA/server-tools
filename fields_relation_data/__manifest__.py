# Copyright 2019 Silvio Gregorini <silviogregorini@openforce.it>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    'name': 'Fields Relation Data',
    'summary': "Show relations data in ir.model.fields tree views",
    'version': '12.0.1.0.0',
    'category': 'Tools',
    'author': 'Openforce, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/server-tools',
    'license': 'AGPL-3',
    'depends': [
        'base'
    ],
    'data': [
        'views/ir_model.xml',
        'views/ir_model_fields.xml',
    ],
    'installable': True,
}
