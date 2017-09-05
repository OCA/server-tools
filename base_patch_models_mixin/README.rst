.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=======================
Base Patch Models Mixin
=======================

This module adds a mixin class which is meant to simplify working with
patches on BaseModel or on abstract models like ``mail .thread``. If you just
change them, models created earlier will lack the attributes you add. Just
inherit from this mixin, it will check which existing models need your
changes and apply them.

Configuration
=============

In your module, do something like::

    class MailThread(models.AbstractModel):
        _name = 'mail.thread'
        _inherit = ['base.patch.models.mixin', 'mail.thread']

in case you need to patch BaseModel, say::

    class BaseModel(models.BaseModel):
        _name = 'my.unique.model.name'
        _inherit = 'base.patch.models.mixin'

Your code will behave as if it was an inherited class of the class you pass
in the second parameter to ``_base_patch_models``.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/9.0

Known issues / Roadmap
======================

* This module must not be ported to v10.0 as the issue does not exist anymore
  in such version or greater.

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

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>
* Lois Rilo <lois.rilo@eficent.com>

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
