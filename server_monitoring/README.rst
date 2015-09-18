.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

=================
server monitoring
=================

This module allows in-database logging of some statistics in order to monitor
the health of an openerp instance.

Database indicators are logged (number of rows, table size, number of reads,
number of updates...), with a cron running each week by default. This cron
needs to be activated after the module is installed.

Some process indicators are logged (cpu time, memory) together with information
about the different XMLRPC calls made to the server (user, model, method).

Two crons are provided to cleanup old logs from the database.


Configuration
=============

To configure this module, you need to:

* Settings -> Scheduled Actions and tune the cron tasks

Usage
=====

Just install the addon in your instance. You will be able to access the logs
under Reporting -> Server Monitoring.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/7.0

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

* Not tested under other platforms than Linux

TODO / WISH list:
* visualization
* export
* check if we can / wish to log session id
* check if we can log pooler state (whatever that is...)
* check if we can log HTTP status
* enhance group by for process logs. 


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20server_monitoring%0Aversion:%207.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Alexandre Fayolle  <alexandre.fayolle@camptocamp.com>

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
