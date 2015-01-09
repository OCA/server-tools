# -*- coding: utf-8 -*-
# =============================================================================
#                                                                             =
#    materialized_sql_view module for OpenERP,                                =
#    Copyright (C) 2013 Anybox (<http://http://anybox.fr>)                    =
#                         Pierre Verkest <pverkest@anybox.fr>                 =
#                                                                             =
#    This file is a part of materialized_sql_view                             =
#                                                                             =
#    materialized_sql_view is free software: you can redistribute it and/or   =
#    modify it under the terms of the GNU Affero General Public License v3 or =
#    later as published by the Free Software Foundation, either version 3 of  =
#    the License, or (at your option) any later version.                      =
#                                                                             =
#    materialized_sql_view is distributed in the hope that it will be useful, =
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           =
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            =
#    GNU Affero General Public License v3 or later for more details.          =
#                                                                             =
#    You should have received a copy of the GNU Affero General Public License =
#    v3 or later along with this program.                                     =
#    If not, see <http://www.gnu.org/licenses/>.                              =
#                                                                             =
# =============================================================================
{
    'name': 'Materialized Sql View',
    'version': '7.0.1.0',
    'category': 'Tools',
    'description': """
=====================
Materialized SQL VIEW
=====================

This odoo module, add utilities to manage materialized SQL view
and necessary user interface to interact with.

How to use it
-------------

You can have a look to `the basic example
<https://github.com/OCA/server-tools/blob/7.0/test_materialized_sql_view/model/
model_test_using_sql_mat_view.py>`_,
used in test module: `test_materialized_sql_view`.

You can etheir add cron to refresh the materialized view periodicly,
`here <https://github.com/OCA/server-tools/blob/7.0/test_materialized_sql_view/
data/ir_cron.xml>`
an example on the previous model


Features
--------

* UI to manage materialized Sql view, and manually launch refresh
    - add `Materialized sql view Manager` group to your expected user.
    - Go through `Settings > Technical > Database Structure >
      Materialized SQL view` menu to manage materialized sql views
* Abstract class, to help developer to create materialized sql view
* Use postgresql materialized view if pg >= 9.3.0.
* Manage when pg version changed
* Recreate materialized sql view only if necessary, one of those change:
  - sql materialized view name `_sql_mat_view_name`, this is used as search key
    (so if you change it, you have to manage how to clean unecessary views and
    records)
  - sql definition has changed `_sql_view_definition`
  - sql view name has changed `_sql_view_name`
  - database version has changed


TODO
----

* Add UI on models based on materialized view. Specialy on dashboards
    """,
    'author': 'Pierre Verkest (Anybox), Odoo Community Association (OCA)',
    'maintainer': 'Odoo Community Association (OCA)',
    'depends': [
        'base',
        'web',
    ],
    'demo_xml': [
    ],
    'data': [
        'security/security_group.xml',
        'security/ir.model.access.csv',
        'views/materialized_sql_view.xml',
        'menus/menus.xml',
    ],
    'js': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
