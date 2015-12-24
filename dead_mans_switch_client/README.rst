.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

==========================
Dead man's switch (client)
==========================

This module is the client part of `dead_mans_switch_server`. It is responsible
of sending the server status updates, which in turn takes action if those
updates don't come in time.

Configuration
=============

After installing this module, you need to fill in the system parameter
``dead_mans_switch_client.url``. This must be the full URL to the server's
controller, usually of the form ``https://your.server/dead_mans_switch/alive``.

This module attempts to send CPU and RAM statistics to the server. While this
is not mandatory, it's helpful for assessing a server's health. If you want
this, you need to install ``psutil``.

You can also have the currently online users logged, but this only works if
the ``im_chat`` module is installed.

Usage
=====

This module doesn't have any visible effect on the client.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
    :alt: Try me on Runbot
    :target: https://runbot.odoo-community.org/runbot/149/8.0

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

* certificate pinning would be nice

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20dead_mans_switch_client%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>
* Jairo Llopis <yajo.sk8@gmail.com>

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
