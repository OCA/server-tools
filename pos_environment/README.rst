.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================================
POS configuration with server_environment
=========================================

This module allows to configure the hardware proxy (PosBox)
using the ``server_environment`` mechanism: you can then have different
hardware proxy for the production and the test environment.

Installation
============

To install this module, you need to have the server_environment module
installed and properly configured.

Configuration
=============

With this module installed, the hardware proxy are configured in
the ``server_environment_files`` module (which is a module
you should provide, see the documentation of ``server_environment`` for
more information).

In the configuration file of each environment, you may use the
section ``[hardware_proxy]`` to configure the
default values respectively for hardware proxy.

Then for each server, you can define additional values or override the
default values with a section named ``[hardware_proxy.resource_name]``
where "resource_name" is the name of the server.

Exemple of config file ::

   [hardware_proxy]
   proxy_ip = 196.101.45.78

   [hardware_proxy.pos_box_01]
   proxy_ip = 158.24.86.95

You will need to create record in the database for pos configuration
with the field ``name`` set to "pos_box_01"


Usage
=====

Once configured, Odoo will read the hardware proxy values from the
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

* Oleksandr Paziuk <oleksandr.paziuk@camptocamp.com>
* Denis Leemann <denis.leemann@camptocamp.com>

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
