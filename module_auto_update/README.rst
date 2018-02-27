.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

==================
Module Auto Update
==================

This addon provides mechanisms to compute sha1 hashes of installed addons,
and save them in the database. It also provides a method that exploits these
mechanisms to update a database by upgrading only the modules for which the
hash has changed since the last successful upgrade.

Configuration
=============

This module supports the following system parameters:

* ``module_auto_update.exclude_patterns``: comma-separated list of file
  name patterns to ignore when computing addon checksums. Defaults to
  ``*.pyc,*.pyo,i18n/*.pot,i18n_extra/*.pot,static/*``.
  Filename patterns must be compatible with the python ``fnmatch`` function.

In addition to the above pattern, .po files corresponding to languages that
are not installed in the Odoo database are ignored when computing checksums.

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

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/9.0

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

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Brent Hughes <brent.hughes@laslabs.com>
* Juan José Scarafía <jjs@adhoc.com.ar>
* Jairo Llopis <jairo.llopis@tecnativa.com>
* Stéphane Bidoul <stephane.bidoul@acsone.eu> (https://acsone.eu)

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
