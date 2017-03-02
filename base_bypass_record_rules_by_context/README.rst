.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================
Bypass Record Rules
===================

This module bypasses permissions on fields visibility by field context.
For example in a multi-company environment it allows to see the records of
company B for a user of company A, even if the user has no visibility on
these records (i.e. B is not an allowed company).

Installation
============

No specific requirements.

Configuration
=============

Add a context ref in a model view for the desired field with the
'bypass_record_rules' key set to 1, for example:

<field name="my_field" context="{'bypass_record_rules':1}">

Usage
=====

No specific requirements.

Known issues / Roadmap
======================

No known issues.

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

* Roberto Onnis <roberto.onnis@innoviu.com>

Funders
-------

The development of this module has been financially supported by:

* Agile Business Group Sagl

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
