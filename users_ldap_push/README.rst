.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

==================
Push users to LDAP
==================

This module was written in order to use Odoo as a frontend for creating LDAP
entries by creating user records. Updates to the user record will be propagated
to the linked LDAP entry afterwards.

When users change their passwords, they will be updated in the LDAP directory
too.

Configuration
=============

On the LDAP parameters of your company, check *Create ldap entry* in order to
activate this functionality. Be sure to configure a bind DN that has
appropriate permissions to create and modify entries.

Fill in the object classes newly created entries should contain, separated by
colons. Those classes will determine which mappings from Odoo fields to LDAP
attributes you need. This is highly dependent on your LDAP setup.

For a standard slapd setup, you might want to use object classes
`inetOrgPerson,shadowAccount` and the following mapping:

========== ============== ==
Odoo field LDAP attribute DN
========== ============== ==
Login      userid         X
Name       cn
Name       sn
========== ============== ==

Matching is done by the new field *ldap_entry_dn*, so after installing this
module, you'll probably want to set this field. The module will write it when
a user logs in via Odoo.

Usage
=====

When you create or update users, their corresponding LDAP entries will be
updated too.

When creating users, there's a checkbox 'LDAP user' which allows you to push
the new user to your LDAP directory. This of course only works if you have
field mappings for all mandatory fields in your schema.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
    :alt: Try me on Runbot
    :target: https://runbot.odoo-community.org/runbot/149/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20users_ldap_push%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
