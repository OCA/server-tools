.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============
Onchange Helper
===============

This is a technical module. Its goal is to ease the play of onchange method directly called from Python code.

Usage
=====

To use this module, you need to:

* depend on this module
* call `yourmodel.play_onchanges(values, ['field'])`

Example if you want to create a sale order and you want to get the values relative to partner_id field (as if you fill the field from UI)

    `vals = {'partner_id': 1}`

    `vals = self.env['sale.order'].play_onchanges(vals, ['partner_id'])`

Then, `vals` will be updated with partner_invoice_id, partner_shipping_id, pricelist_id, etc...

You can also use it on existing record for example:

    `vals = {'partner_shipping_id': 1}`

    `vals = sale.play_onchanges(vals, ['partner_shipping_id'])`

Then the onchange will be played with the vals passed and the existing vals of the sale. `vals` will be updated with partner_invoice_id, pricelist_id, etc..

if you want overwrite values passed in param values by values onchange returned you can use `overwrite_values=True` in context. Ex :

    `vals = {'partner_id': 1, partner_invoice_id: 10}`

    `vals = self.env['sale.order'].with_context(
        overwrite_values=True).play_onchanges(vals, ['partner_id'])`
Then, `vals` will be updated with partner_invoice_id, partner_shipping_id, pricelist_id, etc... partner_invoice_id value will be ovewrited by value
returned by onchange ex partner_invoice_id: 5. Without changing context value
partner_invoice_id keep the first value (i.e 10).

Behind the scene, `play_onchanges` will execute **all the methods** registered for the list of changed fields, so you do not have to call manually each onchange. To avoid performance issue when the method is called on a record, the record will be transformed into a memory record before calling the registered methods to avoid to trigger SQL updates command when values are assigned to the record by the onchange

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

* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Florian da Costa <florian.dacosta@akretion.com>

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

