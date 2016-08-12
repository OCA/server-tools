.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
Disable model translation
=========================

Provides means to globally disable translation of field contents for
all fields on a per Model base.
Overrides `translate=True` of all fields of a model (including inherited
custom fields of other models).

For example to disable translation of all product data (description etc.).
Inherit from `product.product` (and `product.template`) and set class
attribute `self._disable_field_translations` of the model to False.


Installation
============

No specific requirements.


Configuration
=============

To disable translation of all fields for a given model you need to inherit
that model and set class attribute `self._disable_field_translations`
of the model to True.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/serevr-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Peter Hahn <peter.hahn@initos.com>

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
