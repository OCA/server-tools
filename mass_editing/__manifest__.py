# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mass Editing',
    'version': '11.0.1.7.0',
    'author': 'Serpent Consulting Services Pvt. Ltd., '
              'Tecnativa, '
              'Odoo Community Association (OCA),'
              'Codeware Computer Trading LLC',
    'contributors': [
        'Oihane Crucelaegui <oihanecrucelaegi@gmail.com>',
        'Serpent Consulting Services Pvt. Ltd. <support@serpentcs.com>',
        'Jay Vora <jay.vora@serpentcs.com>',
        'Codeware Computer Trading LLC <info@codewareuae.com>',
    ],
    'category': 'Tools',
    'website': 'http://www.serpentcs.com, http://www.codewareuae.com',
    'license': 'GPL-3 or any later version',
    'summary': 'Mass Editing',
    'uninstall_hook': 'uninstall_hook',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/mass_editing_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
