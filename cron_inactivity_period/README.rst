.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

========================
Cron - Inactivity Period
========================


This module allows you to disable cron Jobs during periods.
It can be usefull if you want to disable your cron jobs during maintenance
period, or for other reasons.

Note
----

If you have installed ``cron_run_manually`` module, it is still possible to run
your job, during inactivity periods.

Configuration
=============

To configure this module, you need to:

* Go to Settings > Technical > Automation > Scheduled Actions and select a
  cron

* Add new option inactivity periods

.. figure:: https://raw.githubusercontent.com/OCA/server-tools/8.0/cron_inactivity_period/static/description/ir_cron_form.png
   :alt: Inactivity Period Settings
   :width: 80 %
   :align: center


Known issues / Roadmap
======================

* For the time being, only one type of inactivity period is available. ('hour')
  It should be great to add other options like 'week_day', to allow user to
  disable cron jobs for given week days.


Credits
=======

Authors
~~~~~~~

* GRAP, Groupement Régional Alimentaire de Proximité (http://www.grap.coop)

Contributors
~~~~~~~~~~~~

* Sylvain LE GAL (https://www.twitter.com/legalsylvain)

Maintainers
~~~~~~~~~~~

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.

