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

{
    'name': 'Mail timeout',
    'version': '0.1',
    'category': 'Tools',
    'author': "Camptocamp,Odoo Community Association (OCA)",
    'summary': 'Clean up mails regularly',
    'description': """
.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Mail timeout
===========

This module adds a "timeout" parameter to fetchmail servers.

Configuration
=============

This module depends on ``mail_environment`` in order to add a timeout value
per server.

Example of a configuration file (add those values to your server)::

 [incoming_mail.openerp_pop_mail1]
 timeout = 60

Known issues / Roadmap
======================

* None

Credits
=======

Contributors
------------

* Matthieu Dietrich <matthieu.dietrich@camptocamp.com>

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
    'license': 'AGPL-3',
    'website': 'http://openerp.camptocamp.com',
    'depends': ['mail_environment'],
    'data': ['mail_view.xml'],
    'installable': True,
}
