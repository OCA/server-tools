.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================================
Mail configuration with server_environment
==========================================

This module allows to configure the incoming and outgoing mail servers
using the `server_environment` mechanism: you can then have different
mail servers for the production and the test environment.

Installation
============

To install this module, you need to have the server_environment module
installed and properly configured.

Configuration
=============

With this module installed, the incoming and outgoing mail servers are
configured in the `server_environment_files` module (which is a module
you should provide, see the documentation of `server_environment` for
more information).

In the configuration file of each environment, you may first use the
sections `[outgoing_mail]` and `[incoming_mail]` to configure the
default values respectively for SMTP servers and the IMAP/POP servers.

Then for each server, you can define additional values or override the
default values with a section named `[outgoing_mail.resource_name]` or
`[incoming_mail.resource_name]` where "resource_name" is the name of
the server.

Exemple of config file ::

  [outgoing_mail]
  smtp_host = smtp.myserver.com
  smtp_port = 587
  smtp_user =
  smtp_pass =
  smtp_encryption = ssl

  [outgoing_mail.odoo_smtp_server1]
  smtp_user = odoo
  smtp_pass = odoo

  [incoming_mail.odoo_pop_mail1]
  server = mail.myserver.com
  port = 110
  type = pop
  is_ssl = 0
  attach = 0
  original = 0
  user = odoo@myserver.com
  password = uas1ohV0

You will need to create 2 records in the database, one outgoing mail
server with the field `name` set to "odoo_smtp_server1" and one
incoming mail server with the field `name` set to "odoo_pop_mail1".


Usage
=====

Once configured, Odoo will read the mail servers values from the
configuration file related to each environment defined in the main
Odoo file.


Known issues / Roadmap
======================

* Due to the special nature of this addon, you cannot test it on the OCA
  runbot.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Nicolas Bessi <nicolas.bessi@camptocamp.com>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Joël Grand-Guillaume <joel.grandguillaume@camptocamp.com>
* Holger Brunn <hbrunn@therp.nl>
* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>

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
