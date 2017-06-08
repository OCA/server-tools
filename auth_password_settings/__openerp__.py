# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Dhaval Patel
#    Copyright (C) 2011 - TODAY Denero Team. (<http://www.deneroteam.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'User Password Settings',
    'version': '1.0',
    'category': 'base',
    'sequence': 3,
    'summary': 'User Password Settings',
    'author': 'Denero Team,Odoo Community Association (OCA)',
    'website': 'http://www.deneroteam.com',
    'maintainer': 'Denero Team',
    'license': 'AGPL-3',
    'depends': [
        'base', 'base_setup',
    ],
    'data': [
        # Datas
        "data/auth_password_settings_data.xml",
        # Security

        # Views
        "views/res_config_view.xml",
        # Menus

        # Wizards

    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
