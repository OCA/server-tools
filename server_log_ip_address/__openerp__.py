# -*- coding: utf-8 -*-
###############################################################################
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Arche TI Inc. - http://www.archeti.ca
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': ' Server - Log user IP Address',
    'version': '1.0',
    'category': 'Other',
    'summary': 'Log the user IP Address - aimed to be used with Fail2ban',
    'author': 'Arche TI Inc., Odoo Community Association (OCA)',
    'website': 'https://www.archeti.ca',
    'license': 'AGPL-3',
    'depends': ['base'],
    'external_dependencies': {
        'python': [],
    },
    'installable': True,
    'auto_install': False,
    'demo': [],
    'data': [],
}
