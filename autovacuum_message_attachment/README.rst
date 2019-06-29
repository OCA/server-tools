.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
    :alt: License: LGPL-3

=======================
AutoVacuum Mail Message
=======================

Odoo create a lot of message and/or mails. With time it can slow the system or take a lot of disk space.
The goal of this module is to clean these message once they are obsolete.


Configuration
=============

* Go to the menu configuration => Technical => Email => Message vacuum Rule
* Add the adequates rules for your company. On each rule, you can indicate the models, type and subtypes for which you want to delete the messages, along with a retention time (in days).
* Activate the cron AutoVacuum Mails and Messages

It is recommanded to run it frequently and when the system is not very loaded.
(For instance : once a day, during the night.)


Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/9.0

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

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------

* Florian da Costa <florian.dacosta@akretion.com>

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
