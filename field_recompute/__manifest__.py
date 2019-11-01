# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Field Recompute',
    'version': '12.0.1.0.0',
    'author': 'GRAP,Odoo Community Association (OCA)',
    'website': 'https://www.github.com/OCA/server-tools',
    'license': 'AGPL-3',
    'category': 'Tools',
    'summary': 'Recompute any compute fields',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ir_model_fields_recompute.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/ir_model_fields_recompute.xml',
    ],
    'installable': True,
}
