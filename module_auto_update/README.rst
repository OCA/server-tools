.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

==================
Module Auto Update
==================

Ipmortant note: this module may present reliability issues. 
In particular, the server should restarted before running the upgrade cron.
See https://github.com/OCA/server-tools/issues/1151 and
https://github.com/OCA/server-tools/pull/1176 for more information.
OCA recommands using ``module_checksum_upgrade`` instead.

This module will automatically check for and apply module upgrades on a schedule.

Upgrade checking is accomplished by comparing the SHA1 checksums of currently-installed modules to the checksums of corresponding modules in the addons directories.

Installation
============

Prior to installing this module, you need to:

#. Install checksumdir with `pip install checksumdir`
#. Ensure all installed modules are up-to-date. When installed, this module will assume the versions found in the addons directories are currently installed.

Configuration
=============

The default time for checking and applying upgrades is 3:00 AM (UTC). To change this schedule, modify the "Perform Module Upgrades" scheduled action.

This module will ignore .pyc and .pyo file extensions by default. To modify this, create a module_auto_update.checksum_excluded_extensions system parameter with the desired extensions listed as comma-separated values.

Usage
=====

Modules scheduled for upgrade can be viewed by clicking the "Updates" menu item in the Apps sidebar.

To perform upgrades manually, click the "Apply Scheduled Upgrades" menu item in the Apps sidebar.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/10.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Brent Hughes <brent.hughes@laslabs.com>
* Juan José Scarafía <jjs@adhoc.com.ar>

Do not contact contributors directly about support or help with technical issues.

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
