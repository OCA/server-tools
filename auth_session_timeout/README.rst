.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
Inactive Sessions Timeout
=========================

This module was written to be able to kill(logout) all inactive sessions since
a given delay. On each request the server checks if the session is yet valid
regarding the expiration delay. If not a clean logout is operated.

Configuration
=============

Two system parameters are available:

* ``inactive_session_time_out_delay``: validity of a session in seconds
  (default = 2 Hours)
* ``inactive_session_time_out_ignored_url``: technical urls where the check
  does not occur

Usage
=====

Setup the session parameters as described above.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/11.0

Known issues / Roadmap
======================


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Cédric Pigeon <cedric.pigeon@acsone.eu>
* Dhinesh D <dvdhinesh.mail@gmail.com>
* Jesse Morgan <jmorgan.nz@gmail.com>
* Dave Lasley <dave@laslabs.com>

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
