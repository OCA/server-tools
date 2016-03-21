# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2016 Clear ICT Solutions (<info@clearict.com>).
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
    'name': 'Database content cleanup - HR Time Sheet',
    'summary': 'Remove HR time sheet related content from the database',
    'version': '8.0',
    'author': "Clear ICT Solutions,Odoo Community Association (OCA)",
    'depends': [
        'content_cleanup',
        'hr_timesheet',
    ],
    'license': 'AGPL-3',
    'category': 'Tools',
    'data': [],
    'installable': True,
    'auto_install': False,
}
