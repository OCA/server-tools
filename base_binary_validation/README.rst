.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/LGPL
   :alt: License: LGPL-3

======================
Base binary validation
======================

Provide base validation for binary attachments.

You can:

* validate standard attachments on create/write
* use `BinaryValidated` field to validate them automatically


NOTE: to improve mimetype guessing you should install `libmagic` on you system
since Odoo standard leads to random results.


Batteries not included
----------------------

This module is meant to be used by integrators and developers
to add validation to existing or custom models.
You won't see any change in Odoo after installing it.

Usage
=====

Validate `ir.attachment`
------------------------

You can validate standard attachments by providing `allowed_mimetypes` in context::

  self.env['ir.attachment'].with_context(allowed_mimetypes=('application/pdf')).create({...})


Validate fields w/ `attachment=True`
-----------------------------------

Define your field::

  from odoo.addons.base_binary_validation.fields import BinaryValidated

  class Foo(models.Model):
      [...]

      terms_conditions = BinaryValidated(
          string='Terms and Conditions',
          attachment=True,
          allowed_mimetypes=('application/pdf', ),
      )

In both cases, if `allowed_mimetypes` is not satisfied you'll get a validation error.


Known issues / Roadmap
======================

* Validate non `attachment` binary fields


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------

* Simone Orsi <simone.orsi@camptocamp.com>

Do not contact contributors directly about support or help with technical issues.


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
