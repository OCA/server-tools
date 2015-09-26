# -*- encoding: utf-8 -*-
##############################################################################
#
#    Authentification - Track And Prevent Brute-force Attack module for Odoo
#    Copyright (C) 2015-Today GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
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
##############################################################################

{
    'name': 'Authentification - Brute-force Attack',
    'version': '8.0.1.0.0',
    'category': 'base',
    'summary': "Authentication Tracking and Prevent Brute-force Attack",
    'author': "GRAP,Odoo Community Association (OCA)",
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'web',
        ],
    'data': [
        'data/ir_config_parameter.xml',
        'views/view.xml',
        'views/action.xml',
        'views/menu.xml',
    ],
}
