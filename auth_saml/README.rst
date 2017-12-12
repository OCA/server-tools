.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
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
========

* Reducing the time spent typing different passwords for different accounts.

* Reducing the time spent in IT support for password oversights.

* Centralizing authentication systems.

* Securing all input levels / exit / access to multiple systems without
  prompting users.

* The centralization of access control information for compliance testing to
  different standards.


Installation
============

Install as you would install any Odoo addon.

Dependencies
------------

This addon requires `lasso`_.

.. _lasso: http://lasso.entrouvert.org


Configuration
=============

There are SAML-related settings in Configuration > General settings.


Usage
=====

To use this module, you need an IDP server, properly set up. Go through the
"Getting started" section for more information.


Demo
====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/8.0


Known issues / Roadmap
======================

None for now.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/
{project_repo}/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback `here <https://github.com/OCA/
{project_repo}/issues/new?body=module:%20
{module_name}%0Aversion:%20
{version}%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

In order of appearance:

  - Florent Aide, <florent.aide@xcg-consulting.fr>
  - Vincent Hatakeyama, <vincent.hatakeyama@xcg-consulting.fr>
  - Alexandre Brun, <alexandre.brun@xcg-consulting.fr>
  - Jeremy Co Kim Len, <jeremy.cokimlen@vinci-concessions.com>
  - Houzéfa Abbasbhay <houzefa.abba@xcg-consulting.fr>


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
