.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3

===============
Export Security
===============

This module adds the following security features to Odoo's data exporting:

#. A security group for restricting users' ability to export data
#. A log of exports detailing the user responsible, as well as the model, records, and fields exported
#. A `#data exports` channel for export activity notifications

Screenshots
===========

Hidden Export Menu Item
-----------------------

.. image:: /base_export_security/static/description/export_menu_item_hidden.png?raw=true
   :alt: Hidden Export Menu Item
   :width: 600 px

Export Log
----------

.. image:: /base_export_security/static/description/export_log.png?raw=true
   :alt: Export Log
   :width: 600 px

Channel Notification
--------------------

.. image:: /base_export_security/static/description/export_notification.png?raw=true
   :alt: Export Notification
   :width: 500 px

Configuration
=============

To configure this module, you need to:

#. Add users who require data export rights to the `Export Rights` security group, found in Settings/Users (requires developer mode to be active)
#. Invite users who should receive export activity notifications to the `#data exports` notification channel

Usage
=====

To view detailed Export Logs, go to Settings/Data Exports/Export Logs

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
