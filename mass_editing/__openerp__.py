# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C):
#        2012-Today Serpent Consulting Services (<http://www.serpentcs.com>)
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
    'name': 'Mass Editing',
    'version': '9.0.1.0.0',
    'author': 'Serpent Consulting Services Pvt. Ltd., '
              'Odoo Community Association (OCA)',
    'contributors': [
        'Oihane Crucelaegui <oihanecrucelaegi@gmail.com>',
        'Serpent Consulting Services Pvt. Ltd. <support@serpentcs.com>',
    ],
    'category': 'Tools',
    'website': 'http://www.serpentcs.com',
    'license': 'GPL-3 or any later version',
    'summary': 'Mass Editing',
    'depends': ['base'],
    'images': [],
    'data': [
        'security/ir.model.access.csv',
        'views/mass_editing_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
