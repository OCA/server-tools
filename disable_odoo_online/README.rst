.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==================
Remove odoo.com Bindings
==================

This module deactivates all bindings to odoo.com that come with the standard
code:

* update notifier code is deactivated and the function is overwritten
* apps and updates menu items in settings are hidden inside Tools\\Parameters
* upload thread is deactivated

Installation
============

To install this module, you need to:

* clone the branch 11.0 of the repository https://github.com/OCA/server-tools
* add the path to this repository in your configuration (addons-path)
* update the module list
* search for "Remove odoo.com Bindings" in your addons
* install the module

Configuration
=============

No extra configuration needed.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot

Known issues / Roadmap
======================



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

* Holger Brunn <hbrunn@therp.nl>
* Stefan Rijnhart <stefan@opener.am>
* Sylvain LE GAL (https://twitter.com/legalsylvain)
* Hieu, Vo Minh Bao <hieu.vmb@komit-consulting.com>

Do not contact contributors directly about support or help with technical issues.

Funders
-------

The development of this module has been financially supported by:

* Komit https://komit-consulting.com

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

