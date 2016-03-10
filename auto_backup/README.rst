.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
Database Auto-Backup
====================

A tool for all your back-ups, internal and external!

Installation
============

Before installing this module, you need to execute::

    pip install pysftp

Configuration
=============

Go to *Settings -> Configuration -> Configure Backup* to
create your configurations for each database that you needed
to backups.

Usage
=====

Keep your Odoo data safe with this module. Take automated back-ups,
remove them automatically and even write them to an external server
through an encrypted tunnel. You can even specify how long local backups
and external backups should be kept, automatically!

Connect with an FTP Server
--------------------------

Keep your data safe, through an SSH tunnel!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Want to go even further and write your backups to an external server?
You can with this module! Specify the credentials to the server, specify
a path and everything will be backed up automatically. This is done
through an SSH (encrypted) tunnel, thanks to pysftp, so your data is
safe!

Test connection
---------------

Checks your credentials in one click
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Want to make sure if the connection details are correct and if Odoo can
automatically write them to the remote server? Simply click on the ‘Test
SFTP Connection’ button and you will get message telling you if
everything is OK, or what is wrong!

E-mail on backup failure
------------------------

Stay informed of problems, automatically!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Do you want to know if the database backup succeeded or failed? Subscribe to
the corresponding backup setting notification type.

Run backups when you want
-------------------------

From the backups configuration list, press *More > Execute backup(s)* to
manually execute the selected processes.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20auto_backup%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Yenthe Van Ginneken <yenthe.vanginneken@vanroey.be>
* Alessio Gerace <alessio.gerace@agilebg.com>
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
