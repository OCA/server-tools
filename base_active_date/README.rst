.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================
Base Active Date
================

This module provides an mixin model, active.date, that provides an active
field that is computed, based on a start date and an end date. A cron job
is provided that will recompute the active state every night. There is also
a provision for on the fly recomputation.

For a model to use this mixin, it needs to have a field for a start date and
a field for an end date. Bij default the mixin assumes the names date_start
and date_end for the fields, but this might be overridden.

Fields provided by this mixin
-----------------------------

* active - computed from start- and enddate

A record is active when current date greater then or equal to startdate,
or startdate nt filled, and when date less then enddate or enddate not
filled

Methods provided by this mixin
------------------------------

* _compute_active - will compute active from start- and enddates. Can be
  overridden in inheriting models.
* active_refresh - can be called to recompute active for all records in
  model


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/10.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported.

Images
------

* Odoo Community Association:
  `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Ronald Portier <ronald@therp.nl>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
