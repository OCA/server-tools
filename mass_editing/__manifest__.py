# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mass Editing',
    'version': '10.0.2.1.0',
    'author': 'Serpent Consulting Services Pvt. Ltd., '
              'Tecnativa, '
              'brain-tec AG, '
              'Odoo Community Association (OCA)',
    'contributors': [
        'Oihane Crucelaegui <oihanecrucelaegi@gmail.com>',
        'Serpent Consulting Services Pvt. Ltd. <support@serpentcs.com>',
        'Jay Vora <jay.vora@serpentcs.com>',
        'Raul Martin <raul.martin@braintec-group.com>',
    ],
    'category': 'Tools',
    'website': 'https://github.com/OCA/server-tools'
               '/tree/10.0/mass_editing',
    'license': 'GPL-3 or any later version',
    'summary': 'Mass Editing',
    'uninstall_hook': 'uninstall_hook',
    'depends': ['base', 'mail'],
    "external_dependencies": {
        "python": [
            'openupgradelib'],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/mass_editing_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
