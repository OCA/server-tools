.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================
Base Export Manager
===================

This module extends the export capability:

1. It allows an admin to manage export profiles (``ir.exports``) that
   Odoo stores internally but does not show anywhere.
2. It also adds a new column to access rights to enable/disable export and
   override the export method to check if the user is allowed to export. Export
   is enabled by default.

Configuration
=============

* Activate the developer mode
* Go to Settings > Users > Groups to select a user group
* Edit the group and go to the Access Rights tab
* Uncheck the "Export Access" box on the object of your choice and save

You can also go to Settings > Technical > Security > Access Rights.

Usage
=====

You can create the export profiles as you are used to:

* Go to any list view.
* Check some records.
* Press *More > Export*.
* Use the wizard to choose the columns to export.
* Press *Save fields list*.
* Give it a name.
* Press *OK*.

To manage export profiles, you need to:

* Go to *Settings > Technical > User Interface > Export Profiles*.
* Create a new one.
* Choose a name.
* Choose a model (table in the database).
* Choose the fields to export.

  * If you choose a related field, you can choose also up to 4 levels of
    subfields.
  * You can drag & drop to reorder the fields.

To use one of those profiles, you need to:

* Go to any list view.
* Check some records.
* Press *More > Export*.
* Choose your saved export from *Saved exports*.
* Press *Export to file*.

Once you have configured groups who cannot export an object:

* Connect as a user of this group
* Go to the list view of the object you disabled the export
* Select records and open the Action menu. The "Export" is not there.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/9.0

Known issues / Roadmap
======================

* Translated labels are not used in final exported file.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Javier Iniesta <javieria@antiun.com>
* Antonio Espinosa <antonio.espinosa@tecnativa.com>
* Rafael Blasco <rafael.blasco@tecnativa.com>
* Jairo Llopis <jairo.llopis@tecnativa.com>
* Dave Lasley <dave@laslabs.com>
* Sandip Mangukiya <smangukiya@ursainfosystems.com>
* Maxime Chambreuil <mchambreuil@ursainfosystems.com>

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
