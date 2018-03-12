.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3

=======================
Module Checksum Upgrade
=======================

This addon provides mechanisms to compute sha1 hashes of installed addons,
and save them in the database. It also provides a method that exploits these
mechanisms to update a database by upgrading only the modules for which the
hash has changed since the last successful upgrade.

Usage
=====

The main method provided by this module is ``upgrade_changed_checksum``
on ``ir.module.module``. It runs a database upgrade for all installed
modules for which the hash has changed since the last successful
run of this method. On success it saves the hashes in the database.

The first time this method is invoked after installing the module, it
runs an upgrade of all modules, because it has not saved the hashes yet.
This is by design, priviledging safety. Should this be an issue,
the method ``_save_installed_checksums`` can be invoked in a situation
where one is sure all modules on disk are installed and up-to-date in the
database.

An easy way to invoke this upgrade mechanism is by issuing the following
in an Odoo shell session::

  env['ir.module.module'].upgrade_changed_checksum()

Configuration
=============

This module supports the following system parameters:

* ``module_checksum_upgrade.exclude_patterns``: comma-separated list of file 
  name patterns to ignore when computing addon checksums. Defaults to 
  ``*.pyc,*.pyo,*.pot,static/*``. Filename patterns must be compatible
  with the python ``fnmatch`` function.

In addition to the above pattern, .po files corresponding to languages that
are not installed in the Odoo database are ignored when computing checksums.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------

* Stéphane Bidoul <stephane.bidoul@acsone.eu> (https://acsone.eu)
* Brent Hughes <brent.hughes@laslabs.com>
* Juan José Scarafía <jjs@adhoc.com.ar>
* Jairo Llopis <jairo.llopis@tecnativa.com>

Do not contact contributors directly about support or help with technical issues.

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
