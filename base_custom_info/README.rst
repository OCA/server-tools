.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

================
Base Custom Info
================

This module allows to create custom fields in models without altering model's
structure.

Installation
============

This module serves as a base for other modules that implement this behavior in
concrete models.

This module is a technical dependency and is to be installed in parallel to
other modules.

Usage
=====

This module defines *Custom Info Templates* that define what properties are
expected for a given record.

To define a template, you need to:

* Go to *Settings > Custom Info > Templates*.
* Create one.
* Add some *Properties* to it.

All database records with that template enabled will automatically fill those
properties.

To manage the properties, you need to:

* Go to *Settings > Custom Info > Properties*.

To manage their values, you need to:

* Go to *Settings > Custom Info > Values*.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/135/9.0

Development
===========

To create a module that supports custom information, just depend on this module
and inherit from the ``custom.info`` model.

Known issues / Roadmap
======================

* All data types of custom information values are text strings.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/product-attribute/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Rafael Blasco <rafabn@antiun.com>
* Carlos Dauden <carlos@incaser.es>
* Sergio Teruel <sergio@incaser.es>
* Jairo Llopis <yajo.sk8@gmail.com>

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
