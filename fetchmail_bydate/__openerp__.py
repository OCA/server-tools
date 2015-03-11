# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Innoviu srl (<http://www.innoviu.it>).
#    Copyright (C) 2015 Agile Business Group http://www.agilebg.com
#    @authors
#       Roberto Onnis <roberto.onnis@innoviu.com>
#       Alessio Gerace <alessio.gerace@agilebg.com>
#       Lorenzo Battistini <lorenzo.battistini@agilebg.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################
{
    'name': "Fetchmail by Date",
    "version": "1.0",
    'category': 'Mailing',
    'summary': 'Fetchmail by date and unseen messages',
    'description': """
This module allows to fetch new emails (using IMAP) using their date,
in addition to 'unseen' status.

To enable this, you have to set a 'Last Download Date' in the fetchmail.server
After that, emails with an internal date greater than the saved one will be
downloaded.
""",
    'author': "Innoviu, Agile Business Group, "
              "Odoo Community Association (OCA)",
    'website': 'http://www.innoviu.com',
    'license': 'AGPL-3',
    'depends': ['fetchmail', 'mail'],
    "data": [
        'view/fetchmail_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
