.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

==========================
Base Optional Quick Create
==========================

This module allows to avoid to *quick create* new records, through many2one
fields, for a specific model.
You can configure which models should allow *quick create*.
When specified, the *quick create* option will always open the standard create
form.

Got the idea from https://twitter.com/nbessi/status/337869826028605441

Usage
=====

To use this module, you need to:

 * go into the menu of *ir_model*,
 * select the model for which you want to disable the quick create option,
 * enable the option *Avoid quick create*.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/11.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed
feedback.

Credits
=======

Contributors
------------

* Jonathan Nemry <jonathan.nemry@acsone.eu>
* Lorenzo Battistini <lorenzo.battistini@agilebg.com>
* Alexis de Lattre <alexis.delattre@akretion.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
