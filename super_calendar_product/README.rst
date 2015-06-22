.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Super Calendar - Product
========================

This module was written to extend the functionality of super_calendar. It adds
a new link to a product.

The user benefits:

- a new link to a product, available on super_calendar configurator lines
- a search into super_calendar elements by their product
- a groupby on product_id in the tree view

It can also be displayed in calendar view if the user customizes its
description code during the configuration.

Installation
============

To install this module, you just need to select the module and insure yourself
dependencies are available.

Configuration
=============

No particular configuration to use this module

Usage
=====

To use this module, you need to get an active super_calendar :

- choose a model with a product field (ie; sale.order.line, purchase.order.line, etc.)
- add a product field on your super_calendar configurator line
- search with a product name
- groupby on product

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

This series of modules focus on common Odoo elements (partner, product,
quantity, analytic).
It would be interesting to have a unique dynamic module, but the initial
request of the customer and our budget did not allow us to do so.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20super_calendar_partner%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Agathe Mollé <agathe.molle@savoirfairelinux.com>
* Bruno Joliveau <bruno.joliveau@savoirfairelinux.com>

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
