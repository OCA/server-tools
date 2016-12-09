.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================================
Server Environment Ir Config Parameter
======================================

Override System Parameters from server environment file.
Before using this module, you must be familiar with the
server_environment module.

Installation
============

There is no specific installation instruction for this module.

Configuration
=============

To configure this module, you need to add a section ``[ir.config_parameter]`` to
you server_environment_files configurations, where the keys are the same
as would normally be set in the Systems Parameter Odoo menu.

When first using a value, the system will read it from the configuration file
and override any value that would be present in the database, so the configuration
file has precedence.

When creating or modifying values that are in the configuration file, the
module replace changes, enforcing the configuration value.

For example you can use this module in combination with web_environment_ribbon:

.. code::

   [ir.config_parameter]
   ribbon.name=DEV

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/10.0

Known issues / Roadmap
======================

* When the user modifies System Parameters that are defined in the config
  file, the changes are ignored. It would be nice to display which system
  parameters come from the config file and possibly make their key and value
  readonly in the user interface.

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

* Stéphane Bidoul <stephane.bidoul@acsone.eu>

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
