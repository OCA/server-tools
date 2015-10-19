SAML2 authentication
====================

Let users log into Odoo via an SAML2 provider.

This module allows to deport the management of users and passwords in an
external authentication system to provide SSO functionality (Single Sign On)
between Odoo and other applications of your ecosystem.


WARNING: this module requires auth_crypt. This is because you still have the
    option if not recommended to allow users to have a password stored in odoo
    at the same time as having a SALM provider and id.


Benefits
--------

* Reducing the time spent typing different passwords for different accounts.

* Reducing the time spent in IT support for password oversights.

* Centralizing authentication systems.

* Securing all input levels / exit / access to multiple systems without
  prompting users.

* The centralization of access control information for compliance testing to
  different standards.


Dependencies
------------

This addon requires `lasso`_.

.. _lasso: http://lasso.entrouvert.org
