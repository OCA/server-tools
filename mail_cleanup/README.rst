.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============
Mail cleanup
============

This module allows to:
* mark e-mails older than x days as read,
* move those messages in a specific folder,
* remove messages older than x days
on IMAP servers, just before fetching them.

Since the main "mail" module does not mark unroutable e-mails as read,
this means that if junk mail arrives in the catch-all address without
any default route, fetching newer e-mails will happen after re-parsing
those unroutable e-mails.

Configuration
=============

This module depends on ``mail_environment`` in order to add "expiration dates"
per server.

Example of a configuration file (add those values to your server)::

 [incoming_mail.openerp_imap_mail1]
 cleanup_days = False # default value
 purge_days = False # default value
 cleanup_folder = NotParsed # optional parameter

Known issues / Roadmap
======================

* None

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20mail_cleanup%0Aversion:%209.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Matthieu Dietrich <matthieu.dietrich@camptocamp.com>

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

