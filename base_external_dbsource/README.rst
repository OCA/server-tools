.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

=========================
External Database Sources
=========================

This module allows you to define connections to foreign databases using ODBC, Firebird,
Oracle Client or SQLAlchemy.

Installation
============

No installation required.

Configuration
=============

Database sources can be configured in Settings > Configuration -> Data sources.

Usage
=====

To use this module:
-------------------

* Go to Settings > Database Structure > Database Sources
* Click on Create to enter the following information:

* Data source name 
* Password
* Connector: Choose the database to which you want to connect
* Connection string: Specify how to connect to database

To extend this module:
----------------------


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/10.0 for server-tools

Known issues / Roadmap
======================

* Find a way to remove or default the CA certs dir
* Add concept of multiple connection strings for one source (multiple nodes)
* Add a ConnectionEnvironment that allows for the reuse of connections
* Message box should be displayed instead of error in ``connection_test``
* Remove old api compatibility layers (v11)
* Instead of returning list of results, we should return iterators. This will support
  larger datasets in a more efficient manner.
* Implement better CRUD handling


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Daniel Reis <dreis.pt@hotmail.com>
* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
* Gervais Naoussi <gervaisnaoussi@gmail.com>
* Michell Stuttgart <michellstut@gmail.com>
* Dave Lasley <dave@laslabs.com>

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
