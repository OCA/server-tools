# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>)
#    All Rights Reserved
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
    'name': 'Email gateway - folders',
    'summary': 'Attach mails in an IMAP folder to existing objects',
    'version': '1.0',
    'author': 'Therp BV',
    'website': 'http://www.therp.nl',
    "category": "Tools",
    "depends": ['fetchmail'],
    'data': [
        'view/fetchmail_server.xml',
        'wizard/attach_mail_manually.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'active': True,
}
