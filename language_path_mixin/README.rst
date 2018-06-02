.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Language path mixin
===================
This is a technical module to restore the possibility of Odoo to print RML
reports in other languages than the user's language (for instance, the
customer's language in the case of a sale order).

Odoo 8.0 has lost that capability due to an unlucky combination of technical
aspects of the deprecated RML report functionality and the new API. While the
static content of the report is translated fine, any translatable fields will
still be rendered in the language of the user.

See https://github.com/odoo/odoo/issues/7301 for the original bug report.

This module provides a tool for developers to work around this bug in their
Python code.

Configuration
=============

With a dependency on this module, you can have any model inherit from the mixin
model in your python class definition. You can then assign your class a
*_language_path* member to indicate where to find the language into which its
reports are to be translated. See the following code example:

.. code::

    class SaleOrder(models.Model):
        _name = 'sale.order'
        _inherit = ['sale.order', 'language.path.mixin']
        _language_path = 'partner_id.lang'

In RML reports for such a model, you can then iterate over the records in the
correct language using

    [[ repeatIn(objects.with_language_path(), 'o') ]]

Usage
=====

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

* Kudos if you find a way to do this more elegantly, preferably with a simple
  bugfix in the Odoo core

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20language_path_mixin%0Aversion:%201.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Stefan Rijnhart <stefan@therp.nl>
* Holger Brunn <hbrunn@therp.nl>

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
