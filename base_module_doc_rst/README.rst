.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License AGPL-3

=================================================================================================
This module generates the Technical Guides of selected modules in Restructured Text format (RST).
=================================================================================================

Originally developed by OpenERP SA, migrated from the OpenERP version 6.1 to Odoo version 8.0
by the Odoo Community Association.

    * It uses the Sphinx (http://sphinx.pocoo.org) implementation of RST
    * It creates a tarball (.tgz file suffix) containing an index file and one file per module
    * Generates Relationship Graph

It performs its actions only on the modules that are actually installed in the same database
(being available in the module list is not enough).

Installation
============

* The module automatically takes care of its dependencies and is ready for use after the installation

TODO
=======
    * Hide "Relationship Graph" page if module not installed.
    * Raise an exception when clicking on "Generate Relationship..." if the module is not installed.


Credits
=======

Contributors
------------

* OpenERP SA <http://www.odoo.com>
* Matjaž Mozetič <m.mozetic@matmoz.si>

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20base_module_doc_rst%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

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