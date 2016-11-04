# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Mass Sorting',
    'version': '1.0',
    'author': 'GRAP,Odoo Community Association (OCA)',
    'category': 'Tools',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    "description": """
Mass Sorting
============

This module provides the functionality to sort an one2many fields in any model.

Typically, you can sort sale order line on a sale order, using any fields.

See screenshots in the description folder.

This module is highly inspired by 'mass_editing' module. (by OCA and SerpentCS)
    """,
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/mass_sort_config_view.xml',
        'views/mass_sort_wizard_view.xml',
        'views/action.xml',
        'views/menu.xml',
    ],
    'images': [
        'static/description/1_mass_sort_config.png',
        'static/description/2_button.png',
        'static/description/3_mass_sort_wizard.png',
        'static/description/3_mass_sort_wizard_custom.png',
        'static/description/4_before.png',
        'static/description/5_after.png',
    ],
}
