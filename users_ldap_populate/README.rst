.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

=============
LDAP Populate
=============

This module allows to prepopulate the user database with all entries in the
LDAP database.

Installation
============

In order to schedule the population of the user database on a regular basis,
create a new scheduled action with the following properties:

- Object: res.company.ldap
- Function: action_populate
- Arguments: ``[res.company.ldap.id]``

Substitute ``res.company.ldap.id`` with the actual id of the res.company.ldap
object you want to query.

Usage
=====

To use this module, you need to:

* go to your company settings
* open your LDAP configuration
* click the button ``Populate``

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
    :alt: Try me on Runbot
    :target: https://runbot.odoo-community.org/runbot/149/8.0

For further information, please visit:

* https://www.odoo.com/forum/help-1

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/users_ldap_populate/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/users_ldap_populate/issues/new?body=module:%20users_ldap_populate%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>
* Daniel Reis <dgreis@sapo.pt>
* Stefan Rijnhart <stefan@opener.am>

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
