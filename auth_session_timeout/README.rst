.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Inactive Sessions Timeout
=========================

This module was written to be able to kill(logout) all inactive sessions since
a given delay. On each request the server checks if the session is yet valid
regarding the expiration delay. If not a clean logout is operated.

Configuration
=============

Two system parameters are available:

* inactive_session_time_out_delay: validity of a session in seconds (default = 2 Hours)
* inactive_session_time_out_ignored_url: technical urls where the check does not occur

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20auth_session_timeout%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Cédric Pigeon <cedric.pigeon@acsone.eu>
* Dhinesh D <dvdhinesh.mail@gmail.com>
* Jesse Morgan <jmorgan.nz@gmail.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
