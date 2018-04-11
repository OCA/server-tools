.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============================================================
Tracks Authentication Attempts and Prevents Brute-force Attacks
===============================================================

This module registers each request done by users trying to authenticate into
Odoo. If the authentication fails, a counter is increased for the given remote
IP. After a defined number of attempts, Odoo will ban the remote IP and
ignore new requests.
This module applies security through obscurity
(https://en.wikipedia.org/wiki/Security_through_obscurity),
When a user is banned, the request is now considered as an attack. So, the UI
will **not** indicate to the user that his IP is banned and the regular message
'Wrong login/password' is displayed.

This module realizes a call to a web API (http://ip-api.com) to try to have
extra information about remote IP.

Configuration
=============

Once installed, you can change the ir.config_parameter value for the key
'auth_brute_force.max_attempt_qty' (10 by default) that define the max number
of attempts allowed before the user was banned.

Usage
=====

Admin user have the possibility to unblock a banned IP.

Logging
-------

This module generates some WARNING logs, in the three following cases:

* Authentication failed from remote '127.0.0.1'. Login tried : 'admin'.
  Attempt 1 / 10.

* Authentication failed from remote '127.0.0.1'. The remote has been banned.
  Login tried : 'admin'.

* Authentication tried from remote '127.0.0.1'. The request has been ignored
  because the remote has been banned after 10 attempts without success. Login
  tried : 'admin'.

Screenshot
----------

**List of Attempts**

.. image:: /auth_brute_force/static/description/screenshot_attempts_list.png

**Detail of a banned IP**

.. image:: /auth_brute_force/static/description/screenshot_custom_ban.png


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
:alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/10.0

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

* Remove 🐒 patch for https://github.com/odoo/odoo/issues/24183 when fixed.

* Depending of server and / or user network configuration, the idenfication
  of the user can be wrong, and mainly in the following cases:

  * If the Odoo server is behind an Apache / NGinx proxy and it is not properly
    configured, all requests will use the same IP address. Blocking such IP
    could render Odoo unusable for all users! **Make sure your logs output the
    correct IP for werkzeug traffic before installing this addon.**

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Sylvain LE GAL (https://twitter.com/legalsylvain)
* David Vidal <david.vidal@tecnativa.com>
* Jairo Llopis <jairo.llopis@tecnativa.com>

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
