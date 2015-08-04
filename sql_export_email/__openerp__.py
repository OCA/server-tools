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
    "name": "SQL export email addon",
    "version": "0.1",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "category": "Other",
    "website": "http://www.acsone.eu",
    "depends": ['email_template',
                'sql_export',
                'base_export_email',
                ],
    "description": """

SQL export email addon
=========================

Add server action type to send by email a sql export
For this new action type you need to fill the following fields :
- SQL export : it defines the SQL export to use to get the data.
- Template : it is the mail template to send the email.

Example of use : in a cron for a periodic export of some data
                 to see the evolution.

""",
    "data": ["ir_actions_view.xml"],
    "demo": [],
    "test": [],
    "active": False,
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "application": False,
}
