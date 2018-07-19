.. image:: https://img.shields.io/badge/licence-GPL--3-blue.svg
   :target: http://www.gnu.org/licenses/gpl-3.0-standalone.html
   :alt: License: GPL-3

==================
Server Environment
==================

This module provides a way to define an environment in the main Odoo
configuration file and to read some configurations from files
depending on the configured environment: you define the environment in
the main configuration file, and the values for the various possible
environments are stored in the ``server_environment_files`` companion
module.

The ``server_environment_files`` module is optional, the values can be set using
an environment variable with a fallback on default values in the database.

The configuration read from the files are visible under the Configuration
menu.  If you are not in the 'dev' environment you will not be able to
see the values contained in the defined secret keys
(by default : '*passw*', '*key*', '*secret*' and '*token*').

Installation
============

By itself, this module does little. See for instance the
``mail_environment`` addon which depends on this one to allow configuring
the incoming and outgoing mail servers depending on the environment.

You can store your configuration values in a companion module called
``server_environment_files``. You can copy and customize the provided
``server_environment_files_sample`` module for this purpose. Alternatively, you
can provide them in environment variables ``SERVER_ENV_CONFIG`` and
``SERVER_ENV_CONFIG_SECRET``.


Configuration
=============

To configure this module, you need to edit the main configuration file
of your instance, and add a directive called ``running_env``. Commonly
used values are 'dev', 'test', 'production'::

  [options]
  running_env=dev

Values associated to keys containing 'passw' are only displayed in the 'dev'
environment.

You have several possibilities to set configuration values:

server_environment_files
------------------------

You can edit the settings you need in the ``server_environment_files`` addon. The
``server_environment_files_sample`` can be used as an example:

* values common to all / most environments can be stored in the
  ``default/`` directory using the .ini file syntax;
* each environment you need to define is stored in its own directory
  and can override or extend default values;
* you can override or extend values in the main configuration
  file of your instance;

Environment variable
--------------------

You can define configuration in the environment variable ``SERVER_ENV_CONFIG``
and/or ``SERVER_ENV_CONFIG_SECRET``. The 2 variables are handled the exact same
way, this is only a convenience for the deployment where you can isolate the
secrets in a different, encrypted, file. They are multi-line environment variables
in the same configparser format than the files.
If you used options in ``server_environment_files``, the options set in the
environment variable overrides them. 

The options in the environment variable are not dependent of ``running_env``,
the content of the variable must be set accordingly to the running environment.

Example of setup:

A public file, containing that will contain public variables::

    # These variables are not odoo standard variables,
    # they are there to represent what your file could look like
    export WORKERS='8'
    export MAX_CRON_THREADS='1'
    export LOG_LEVEL=info
    export LOG_HANDLER=":INFO"
    export DB_MAXCONN=5

    # server environment options
    export SERVER_ENV_CONFIG="
    [storage_backend.my-sftp]
    sftp_server=10.10.10.10
    sftp_login=foo
    sftp_port=22200
    directory_path=Odoo
    "

A second file which is encrypted and contains secrets::

    # This variable is not an odoo standard variable,
    # it is there to represent what your file could look like
    export DB_PASSWORD='xxxxxxxxx'
    # server environment options
    export SERVER_ENV_CONFIG_SECRET="
    [storage_backend.my-sftp]
    sftp_password=xxxxxxxxx
    "

Default values
--------------

When using the ``server.env.mixin`` mixin, for each env-computed field, a
companion field ``<field>_env_default`` is created. This field is not
environment-dependent. It's a fallback value used when no key is set in
configuration files / environment variable.

When the default field is used, the field is made editable on Odoo.

Note: empty environment keys always take precedence over default fields


Keychain integration
--------------------

Read the documentation of the class `models/server_env_mixin.py
<models/server_env_mixin.py>`_.


Usage
=====

You can include a mixin in your model and configure the env-computed fields
by an override of ``_server_env_fields``.

::

    class StorageBackend(models.Model):
        _name = "storage.backend"
        _inherit = ["storage.backend", "server.env.mixin"]

        @property
        def _server_env_fields(self):
            return {"directory_path": {}}

Read the documentation of the class and methods in `models/server_env_mixin.py
<models/server_env_mixin.py>`__.


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
