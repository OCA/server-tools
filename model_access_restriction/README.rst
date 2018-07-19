.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl.html
   :alt: License: LGPL-3

======================
Access restriction
======================

This module add a layer of security for CRUD operations.
You can allow some security groups to execute some CRUD action on specific models.
Users who aren't into these groups will have an Access Denied error message.

Others security rules (ir.model.access and ir.rule) are not bypassed.
So first, the system will check standard security access and then (if the access is
allowed), check on access.restriction are executed.

Configuration
=============

Configure Access restrictions in Settings => Security => Access restriction

Example
=============

Into the configuration, add this new Access restriction:
- Model: product.product
- Name: Test product product
- Read: True
- Create: False
- Write: False
- Unlink: False
- Groups: A fictive 'Product Manager' group

If a user try to read a product.product (via form view for example), an error
message will appears for the user (if he is not into the group).
This error message will appears also if you're into a sale.order view (for example).

If you add the user into this 'Product Manager' group, the user will be able
to display product.product.

As other security access are not ignored, if the user is into the
'Product Manager' group, other security check can constrain the user to do
an action.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------

* François Honoré <francois.honore@acsone.eu>

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
