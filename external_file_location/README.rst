.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================
External File Location
======================

This module was written to extend the functionality of ir.attachment to support remote communication and allow you to import/export file to a remote server.
For now, FTP, SFTP and local filestore are handled by the module.

Installation
============

To install this module, you need to:

* fs python module at version 0.5.4 or under
* Paramiko python module

Usage
=====

To use this module, you need to:

* Add a location with your server infos
* Create a task with your file info and remote communication method
* A cron task will trigger each task

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/9.0

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

* Valentin CHEMIERE <valentin.chemiere@akretion.com>
* Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
* Florian DA COSTA <florian.dacosta@akretion.com>
* CArlos Almeida <carlos.almeida@tkobr.com>

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
