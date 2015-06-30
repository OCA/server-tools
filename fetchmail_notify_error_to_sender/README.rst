.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Send notice on fetchmail errors
===============================

If fetchmail is not able to correctly route an email, the email is "silently" lost (you get an error message in server log).
For example, if you configure odoo mail system to route received emails according to recipient address, it may happen users send emails to wrong email address.

This module allows to automatically send a notification email to sender, when odoo can't correctly process the received email.


Configuration
=============

Configure your fetchmail server setting 'Error notice template' = 'Fetchmail - error notice'.
You can edit the 'Fetchmail - error notice' email template according to your needs.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20fetchmail_notify_error_to_sender%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Lorenzo Battistini <lorenzo.battistini@agilebg.com>

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
