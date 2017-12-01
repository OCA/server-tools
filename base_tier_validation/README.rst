.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

====================
Base Tier Validation
====================

This module does not provide a functionality by itself but an abstract model
to implement a validation process based on tiers on other models (e.g.
purchase orders, sales orders...).

**Note:** To be able to use this module in a new model you will need some
development.

See `purchase_tier_validation <https://github
.com/OCA/purchase-workflow>`_ as an example of implementation.

Configuration
=============

To configure this module, you need to:

#. Go to *Settings > Technical > Tier Validations > Tier Definition*.
#. Create as many tiers as you want for any model having tier validation
   functionality.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/9.0

Known issues / Roadmap
======================

* In odoo v11 it would be interesting to try to take advantage of ``mail.activity.mixin``.

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
