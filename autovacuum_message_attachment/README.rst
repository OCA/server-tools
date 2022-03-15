======================================
AutoVacuum Mail Message and Attachment
======================================

Odoo create a lot of message and/or mails. With time it can slow the system or take a lot of disk space.
The goal of this module is to clean these message once they are obsolete.
The same may happen with attachment that we store.
You can choose various criteria manage which messages you want to delete automatically.

**Table of contents**

.. contents::
   :local:

Configuration
=============

* Go to the menu configuration => Technical => Email => Message And Attachment Vacuum Rules
* Add the adeguate rules for your company. On each rule, you can indicate the models, type and subtypes for which you want to delete the messages, along with a retention time (in days). Or for attachment, you can specify a substring of the name.
* Customize the maximum number of records can be deleted on each execution of the vacuum process, by modifying the last parameter in respective crons AutoVacuum Mails and Messages and AutoVacuum Attachments.
* Activate the cron AutoVacuum Mails and Messages and/or AutoVacuum Attachments

It is recommended to run it frequently and when the system is not very loaded.
(For instance : once a day, during the night.)

Known issues / Roadmap
======================

You have to be careful with rules regarding attachment deletion because Odoo find the attachment to delete with their name.
Odoo will find all attachments containing the substring configured on the rule, so you have to be specific enough on the other criteria (concerned models...) to avoid unwanted attachment deletion.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed
`feedback <https://github.com/OCA/server-tools/issues/new?body=module:%20autovacuum_message_attachment%0Aversion:%2012.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* Akretion

Contributors
~~~~~~~~~~~~

* Florian da Costa <florian.dacosta@akretion.com>
* Enric Tobella <etobella@creublanca.es>
* Vincenzo Terzulli <v.terzulli@elvenstudio.it>

Maintainers
~~~~~~~~~~~

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

This module is part of the `OCA/server-tools <https://github.com/OCA/server-tools/tree/8.0/autovacuum_message_attachment>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
