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

No manual configuration is needed.

Usage
=====

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

Credits
=======

Contributors
------------

* Enric Tobella <etobella@creublanca.es>

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
