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

You can use these configuration parameters that control this addon behavior:

* ``auth_brute_force.whitelist_remotes`` is a comma-separated list of
  whitelisted IPs. Failures from these remotes are ignored.

* ``auth_brute_force.max_by_ip`` defaults to 50, and indicates the maximum
  successive failures allowed for an IP. After hitting the limit, the IP gets
  banned.

* ``auth_brute_force.max_by_ip_user`` defaults to 10, and indicates the
  maximum successive failures allowed for any IP and user combination.
  After hitting the limit, that user and IP combination is banned.

Usage
=====

Admin user have the possibility to unblock a banned IP.

Logging
-------

This module generates some WARNING logs, in the following cases:

* When the IP limit is reached: *Authentication failed from remote 'x.x.x.x'.
  The remote has been banned. Login tried: xxxx.*

* When the IP+user combination limit is reached:
  *Authentication failed from remote 'x.x.x.x'.
  The remote and login combination has been banned. Login tried: xxxx.*

Screenshot
----------

**List of Attempts**

.. image:: /auth_brute_force/static/description/screenshot_attempts_list.png


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/10.0

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

* Remove 🐒 patch for https://github.com/odoo/odoo/issues/24183 in v12.

* Depending of server and / or user network configuration, the idenfication
  of the user can be wrong, and mainly in the following cases:

  * If the Odoo server is behind an Apache / NGinx proxy and it is not properly
    configured, all requests will use the same IP address. Blocking such IP
    could render Odoo unusable for all users! **Make sure your logs output the
    correct IP for werkzeug traffic before installing this addon.**

* The IP metadata retrieval should use a better system. `See details here
  <https://github.com/OCA/server-tools/pull/1219/files#r187014504>`_.

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
