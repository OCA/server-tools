.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================
Users LDAP No Reset
===================

This module extends the functionality of auth_signup by preventing password
reset for ldap users. These users should reset their passwords directly in
ldap (for instance Windows domain users can reset their password, and this
will be set in Active Directory).

When a password reset request is entered in the browser, and the user is
an ldap user, a mail will be sent explaining the proper way to reset the
password is through the ldap server. No direct feedback is provided to prevent
website visitors from finding out the login names of internal users.

The email sent to users will probably need to be editted to reflect the
particular procedure to reset passwords for the installation.

Installation
============

To install this module, you need to:

#. Install the module users_ldap_no_reset from the module list.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

* Therp BV

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

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
