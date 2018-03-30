# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
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
    "name" : "Fetch mail into inbox (invoice specific)",
    "version" : "1.0",
    "author" : "Therp BV",
    "complexity": "normal",
    "description": """
Fetch emails from a mail server in order to create invoices from them,
but leave them in the inbox for an user to review those mails manually,
attach them to existing invoices or create new ones.

Usage
=====

Create a fetchmail configuration for the model "Fetchmail inbox for
invoices". The mails fetched from this server will be put into
Invoicing / Customers / Fetchmail inbox for further processing.
    """,
    "category" : "Accounting & Finance",
    "depends" : [
        'account',
        'fetchmail_inbox',
        'fetchmail_invoice',
    ],
    "data" : [
        'view/mail_message.xml',
        'view/menu.xml',
        'security/ir.model.access.csv',
    ],
    "js": [
    ],
    "css": [
    ],
    "qweb": [
    ],
    "auto_install": False,
    "installable": True,
    "external_dependencies" : {
        'python' : [],
    },
}
