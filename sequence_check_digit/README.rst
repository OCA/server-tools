.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License: LGPL-3

====================
Sequence Check Digit
====================

This module was written to configure check digits on sequences added on the end.
It is useful as a control of the number on visual validation.

It is useful when some manual checks are required or on integrations.
The implemented codes can avoid modification of one character and flip of
two consecutive characters.

Configuration
=============

* Access sequences and configurate the model to use.
* The model will check if the format of prefix, suffix and number is valid
* Implemented algorithms
    * Luhn: [0-9]*
    * Damm: [0-9]*
    * Verhoeff: [0-9]*
    * ISO 7064 Mod 11, 2: [0-9]*
    * ISO 7064 Mod 11, 10: [0-9]*
    * ISO 7064 Mod 37, 2: [0-9A-Z]*
    * ISO 7064 Mod 37, 36: [0-9A-Z]*
    * ISO 7064 Mod 97, 10: [0-9A-Z]*

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/9.0

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

* Enric Tobella <etobella@creublanca.es>
* Thomas Binsfeld <thomas.binsfeld@acsone.eu> (https://www.acsone.eu/)

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
