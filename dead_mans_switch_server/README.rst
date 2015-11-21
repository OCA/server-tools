.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

==========================
Dead man's switch (server)
==========================

This module receives status messages by `dead_mans_switch_client` and notifies
you if a client instance didn't check back in time.

As a side effect, you'll also get some statistical data from your client
instances.

Usage
=====

Install `dead_mans_switch_client` on a customer instance and configure it as
described in that module's documentation. The clients will register themselves
with the server automatically. They will show up with their database uuid,
you'll have to assign a human readable description yourself.

At this point, you can assign a customer to this client instance for reporting
purposes, and, more important, add followers to the instance. They will be
notified in case the instance doesn't check back in time. Notification are only
turned on for instances in state 'active', instances in states 'new' or
'suspended' will be ignored.

You'll find the instances' current state at Reporting/Customer instances.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
    :alt: Try me on Runbot
    :target: https://runbot.odoo-community.org/runbot/149/8.0

For further information, please visit:

* https://www.odoo.com/forum/help-1

Security considerations
=======================

As the controller receiving status updates is unauthenticated, any internet user
can have your server create monitoring instance records. While this is annoying,
it's quite harmless and basically the same as misuse of the fetchmail module.

For a more substantial annoyance, the attacker would have to guess one of your
client's database uuids, so they functionally are your passwords.

To be sure, consider blocking this controller from unknown origins in your SSL
proxy. In nginx, it would look like this::

    location /dead_mans_switch/alive {
    allow   192.168.1.0/24;
    # add other client's IPs
    deny    all;
    }

Known issues / Roadmap
======================

* matching is done via the database's uuid, so take care to change this if you
  clone a database
* logging some postgres stats and disk usage would be nice too

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20dead_mans_switch_server%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>

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
