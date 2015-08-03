# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Laetitia Gangloff
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
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
    "name": "Base export email addon",
    "version": "0.1",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "category": "Other",
    "website": "http://www.acsone.eu",
    "depends": ['email_template',
                ],
    "description": """

Base export email addon
=========================

Add server action type to send by email a data export
For this new action type you need to fill the following fields :
- Filter : it defines the filter to use on the data.
- Template : it is the mail template to send the email.
- Saved export : it is a saved export list.
- Fields to export : it is the list of field to export. It can be used alone
                     or to complete the saved export list.

Example of use : in a cron for a periodic export of some data
                 to see the evolution.

""",
    "data": ["ir_actions_view.xml",
             "ir_actions_data.xml"],
    "demo": [],
    "test": [],
    "active": False,
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "application": False,
}
