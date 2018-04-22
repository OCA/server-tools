.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

LDAP groups assignment
======================

Adds user accounts to groups based on rules defined by the administrator.

Usage
=====

Define mappings in Settings / General Settings / LDAP Parameters

Decide whether you want only groups mapped from ldap (`Only ldap groups` checked) or a mix of manually set groups and ldap groups (`Only ldap groups` unchecked). Setting this to 'no' will result in users never losing privileges when you remove them from a ldap group, so that's a potential security issue. It is still the default to prevent losing group information by accident.

For active directory, use LDAP attribute 'memberOf' and operator 'contains'. Fill in the DN of the windows group as value and choose an Odoo group users with this windows group are to be assigned to.

For posix accounts, use operator 'query' and a value like::

    (&(cn=bzr)(objectClass=posixGroup)(memberUid=$uid))

The operator query matches if the filter in value returns something, and value
can contain ``$attribute`` which will be replaced by the first value of the
user's ldap record's attribute named `attribute`.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20{module_name}%0Aversion:%20{version}%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>
* Giacomo Spettoli <giacomo.spettoli@gmail.com>

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
