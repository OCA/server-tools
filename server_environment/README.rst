.. image:: https://img.shields.io/badge/licence-GPL--3-blue.svg
   :target: http://www.gnu.org/licenses/gpl-3.0-standalone.html
   :alt: License: GPL-3

==================
server environment
==================

This module provides a way to define an environment in the main Odoo
configuration file and to read some configurations from files
depending on the configured environment: you define the environment in
the main configuration file, and the values for the various possible
environments are stored in the `server_environment_files` companion
module.

All the settings will be read only and visible under the Configuration
menu.  If you are not in the 'dev' environment you will not be able to
see the values contained in the defined secret keys
(by default : '*passw*', '*key*', '*secret*' and '*token*').

Installation
============

By itself, this module does little. See for instance the
`mail_environment` addon which depends on this one to allow configuring
the incoming and outgoing mail servers depending on the environment.

To install this module, you need to provide a companion module called
`server_environment_files`. You can copy and customize the provided
`server_environment_files_sample` module for this purpose.


Configuration
=============

To configure this module, you need to edit the main configuration file
of your instance, and add a directive called `running_env`. Commonly
used values are 'dev', 'test', 'production'::

  [options]
  running_env=dev

You should then edit the settings you need in the
`server_environment_files` addon. The
`server_environment_files_sample` can be used as an example:

* values common to all / most environments can be stored in the
  `default/` directory using the .ini file syntax;
* each environment you need to define is stored in its own directory
  and can override or extend default values;
* finally, you can override or extend values in the main configuration
  file of you instance.

Values associated to keys
containing 'passw' are only displayed in the 'dev' environment.

Usage
=====

To use this module, in your code, you can follow this example::

    from openerp.addons.server_environment import serv_config
    for key, value in serv_config.items('external_service.ftp'):
       print (key, value)

    serv_config.get('external_service.ftp', 'tls')



.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/10.0


Known issues / Roadmap
======================

* it is not possible to set the environment from the command line. A
  configuration file must be used.
* the module does not allow to set low level attributes such as database server, etc.


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

* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
* Daniel Reis <dgreis@sapo.pt>
* Florent Xicluna <florent.xicluna@gmail.com>
* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Holger Brunn <hbrunn@therp.nl>
* Joël Grand-Guillaume <joel.grandguillaume@camptocamp.com>
* Nicolas Bessi <nicolas.bessi@camptocamp.com>
* Wingo
* Yannick Vaucher <yannick.vaucher@camptocamp.com>


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
