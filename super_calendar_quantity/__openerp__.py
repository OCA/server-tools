# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
    'name': 'Super Calendar - Quantity',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'summary': 'Add new link to quantity for search and groupby on '
               'super_calendar',
    'author': ('Savoir-faire Linux',
               'Odoo Community Association (OCA)'),
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'depends': [
        'super_calendar_partner',
    ],
    'data': [
        'views/super_calendar_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
