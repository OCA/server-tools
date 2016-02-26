
.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
Attachment Metadata
====================

This module extend ir.attachment model with some new fields for a better control
for import and export of files.

The main feature is an integrity file check with a hash.

A file hash is short representation (signature) computed from file data.
Hashes computed before send file and after received file can be compared to be
sure of the content integrity.

An example of the use of this module, can be found in the external_file_location.


Usage
=====

Go the menu Settings > Attachments

You can create / see standard attachments with additional fields



.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/8.0


Known issues / Roadmap
======================

The purpose of this module is not to import the data of the file but only exchange files with external application.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
server-tools/issues/new?body=module:%20
attachment_metadata%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.


Contributors
------------

* Valentin CHEMIERE <valentin.chemiere@akretion.com>
* Sebastien BEAU <sebastian.beau@akretion.com>
* Joel Grand-Guillaume Camptocamp
* initOS <http://initos.com>

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
