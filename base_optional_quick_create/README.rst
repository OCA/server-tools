.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================
Optional quick create
=====================
This module allows to avoid to *quick create* new records, through many2one
fields, for a specific model.
You can configure which models should allow *quick create*.
When specified, the *quick create* option will always open the standard create
form.

Got the idea from https://twitter.com/nbessi/status/337869826028605441

Configuration
=============

To configure this module, you need to go to *Settings -> Database Structure
-> Models. To prevent quick creation on any model, tick *Avoid quick
create* in the form view of these models.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/8.0

Known issues / Roadmap
======================

* If quick creation on the Partner model has been disabled, call the original method if context key 'force_email' is set as this is a special case.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
server-tools/issues/new?body=module:%20
base_optional_quick_create%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Lorenzo Battistini <lorenzo.battistini@agilebg.com>
* Stéphane Bidoul <stephane.bidoul@acsone.eu>
* Alexis de Lattre <alexis@via.ecp.fr>
* Laurent Mignon <laurent.mignon@acsone.eu>
* Stefan Rijnhart <stefan@opener.am>

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
