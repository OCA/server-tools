.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

================
Database cleanup
================

Clean your OpenERP database from remnants of modules, models, columns and
tables left by uninstalled modules (prior to 7.0) or a homebrew database
upgrade to a new major version of OpenERP.

Caution! This module is potentially harmful and can *easily* destroy the
integrity of your data. Do not use if you are not entirely comfortable
with the technical details of the OpenERP data model of *all* the modules
that have ever been installed on your database, and do not purge any module,
model, column or table if you do not know exactly what you are doing.

Usage
=====

After installation of this module, go to the Settings menu -> Technical ->
Database cleanup. Go through the modules, models, columns and tables
entries under this menu (in that order) and find out if there is orphaned data
in your database. You can either delete entries by line, or sweep all entries
in one big step (if you are *really* confident).

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
    :alt: Try me on Runbot
    :target: https://runbot.odoo-community.org/runbot/149/9.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/database_cleanup/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Stefan Rijnhart <stefan@opener.amsterdam>
* Holger Brunn <hbrunn@therp.nl>

Do not contact contributors directly about help with questions or problems concerning this addon, but use the `community mailing list <mailto:community@mail.odoo.com>`_ or the `appropriate specialized mailinglist <https://odoo-community.org/groups>`_ for help, and the bug tracker linked in `Bug Tracker`_ above for technical issues.

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
