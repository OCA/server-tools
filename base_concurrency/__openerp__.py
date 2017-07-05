# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Matthieu Dietrich
#    Copyright 2015 Camptocamp SA
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

{"name": "Base Concurrency",
 "version": "8.0.1.1.0",
 "author": "Camptocamp,Odoo Community Association (OCA)",
 "category": "Specific Module",
 "description": """
Module to regroup all workarounds/fixes to avoid concurrency issues in SQL.

* res.users login_date:
the login date is now separated from res.users; on long transactions,
"re-logging" by opening a new tab changes the current res.user row,
which creates concurrency issues with PostgreSQL in the first transaction.

This creates a new table and a function field to avoid this. In order to
avoid breaking modules which access via SQL the login_date column, a cron
(inactive by default) can be used to sync data.
""",
 "website": "http://camptocamp.com",
 "depends": ['base'],
 "data": ['security/ir.model.access.csv',
          'cron.xml'],
 "auto_install": False,
 "installable": True
 }
