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
    "name" : "Fetch mail into inbox",
    "version" : "1.0",
    "author" : "Therp BV",
    "complexity": "normal",
    "description": """
In some cases, you may not want to have OpenERP create objects directly
on mail arrival, but put them into an inbox for further (possibly manual)
processing.

This module provides the base for this workflow and elementary UI for
processing.

Usage
-----

Create a fetchmail configuration and use 'Fetchmail inbox' as object to be
created on mail arrival. Be sure to check Advanced/Keep original in order
not to lose data in the intermediate step via the inbox.

Mails fetched from this configuration end up in Email/Fetchmail Inbox,
where they can be reviewed and eventually used to create new objects or
attached to existing objects.

Further development
-------------------

This module deals with emails in a very generic way, which is good for
flexibility, but bad for usability. Fortunately, it was developed with
extensibility in mind so that it is very simple to write extension modules
to ease handling emails for specific models in a more user friendly manner.

In simple cases, if you want to force specifying objects of just one model,
you can put 'default_res_model': 'your.model' into the menu action's
context and you're done.
    """,
    "category" : "Dependency",
    "depends" : [
        'mail',
        'fetchmail',
    ],
    "data" : [
        "security/res_groups.xml",
        "wizard/fetchmail_inbox_create_wizard.xml",
        "wizard/fetchmail_inbox_attach_existing_wizard.xml",
        "view/mail_message.xml",
        "view/menu.xml",
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
