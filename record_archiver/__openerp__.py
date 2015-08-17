# -*- coding: utf-8 -*-
#
#    Author: Yannick Vaucher
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

{'name': 'Records Archiver',
 'version': '0.1',
 'description': """
Records Archiver
================

Create a cron job that deactivates old records in order to optimize
performance.

Records are deactivated based on their last activity (write_date).

Configuration
=============

You can configure lifespan of each type of record in
`Settings -> Configuration -> Records Archiver`

A different lifespan can be configured for each model.

Usage
=====

Once the lifespans are configured, the cron will automatically
deactivate the old records.

Known issues / Roadmap
======================

The default behavior is to archive all records having a ``write_date`` <
lifespan and with a state being ``done`` or ``cancel``. If these rules
need to be modified for a model (e.g. change the states to archive), the
hook ``RecordLifespan._archive_domain`` can be extended.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_.  In case of trouble,
please check there if your issue has already been reported.  If you
spotted it first, help us smashing it by providing a detailed and
welcomed feedback `here
<https://github.com/OCA/server-tools/issues/new?body=module:%20record_archiver%0Aversion:%207.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Yannick Vaucher <yannick.vaucher@camptocamp.com>
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
 'author': 'Camptocamp,Odoo Community Association (OCA)',
 'license': 'AGPL-3',
 'category': 'misc',
 'depends': ['base'],
 'website': 'www.camptocamp.com',
 'data': ['views/record_lifespan_view.xml',
          'data/cron.xml',
          'security/ir.model.access.csv',
          ],
 'installable': True,
 'auto_install': False,
 }
