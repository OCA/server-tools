.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Mail timeout
===========

This module adds a "timeout" parameter to fetchmail servers.
Default value is set to 60 seconds.

Configuration
=============

This module depends on ``mail_environment`` in order to add a timeout value
per server.

Example of a configuration file (add those values to your server)::

 [incoming_mail.openerp_pop_mail1]
 timeout = 60 # default value

Known issues / Roadmap
======================

* None

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20mail_timeout%0Aversion:%207.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


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

To contribute to this module, please visit http://odoo-community.org.

