# -*- coding: utf-8 -*-
##############################################################################
#
#    Mass Sorting Module for Odoo
#    Copyright (C) 2016-Today GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
{
    'name': "Mass Sorting",
    'version': "1.0",
    'author': "GRAP,Odoo Community Association (OCA)",
    'category': "Tools",
    'website': "http://www.grap.coop",
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
        "security/ir.model.access.csv",
        'views/mass_sort_config_view.xml',
        'views/mass_sort_wizard_view.xml',
        'views/action.xml',
        'views/menu.xml',
    ],
    'images': [
        'static/description/1_mass_sort_config.png',
        'static/description/2_button.png',
        'static/description/3_mass_sort_wizard.png',
    ],
}
