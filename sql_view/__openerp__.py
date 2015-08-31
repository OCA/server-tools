# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier
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
#

{'name': 'SQL Views',
 'version': '1.0',
 'author': 'Camptocamp,Odoo Community Association (OCA)',
 'license': 'AGPL-3',
 'category': 'Tools',
 'depends': ['base'],
 'description': """
=========
SQL Views
=========

This addon allows to create SQL views on the database.  It also features
a simple CSV export of the views to check their result.

Usage
=====

To create new SQL views, you need to go to ``Settings > Technical >
Database Structure > SQL Views``.

Give a view a human name, a SQL name (which will be prefixed with
``sql_view_`` in the database, and the definition of the view itself
(without trailing semicolon).

Known issues / Roadmap
======================

The CSV preview can be used to read any data on the database. So this
menu **must** be accessible only by allowed admin users. By
default, the module is configured to be accessible only by users having
the ``Settings`` administration level.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and
welcomed feedback
`here
<https://github.com/OCA/server-tools/issues/new?body=module:%20sql_view%0Aversion:%207.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Guewen Baconnier <guewen.baconnier@camptocamp.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
 """,
 'website': 'http://www.camptocamp.com',
 'external_dependencies': {'python': ['unicodecsv']},
 'data': ['wizards/sql_view_csv_preview_views.xml',
          'views/sql_view_views.xml',
          'security/ir.model.access.csv',
          ],
 'installable': True,
 }
