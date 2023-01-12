# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Mass Sorting',
    'version': "10.0.1.0.0",
    'author': 'GRAP,Odoo Community Association (OCA)',
    'summary': 'Sort any models by any fields list',
    'category': 'Tools',
    'website': 'https://github.com/OCA/server-tools'
               '/tree/10.0/mass_sorting',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/view_mass_sort_config.xml',
        'views/view_mass_sort_wizard.xml',
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
    'demo': [
        'demo/mass_sort_config.xml',
        'demo/mass_sort_config_line.xml',
        'demo/function.xml',
    ],
}
