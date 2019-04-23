.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================
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
<https://github.com/OCA/server-tools/issues>`_.  In case of trouble, please
check there if your issue has already been reported.  If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
server-tools/issues/new?body=module:%20
record_archiver%0Aversion:%20
9.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


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
