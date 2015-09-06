.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================
Restrict changing own password
==============================

This module prevents regular users from changing their own passwords.

* Only users in *Access Rights* group (or higher) can change passwords.
* Therefore, this module restricts users without any administration privileges
  to change any password, including their own.
* This behaviour is achieved by hiding the "Change password" button,
  but also enforced within business logic code with a user's group check.
* *admin* user is always allowed to change passwords.

Usage
=====

To use this module, you need to:

* Just install it.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/8.0

For further information, please visit:

* https://www.odoo.com/forum/help-1


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20password_change_restrict%0Aversion:%208.0.1.0.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**%0A>`_.


Credits
=======

Contributors
------------

* Alejandro Santana <alejandrosantana@anubia.es>

Font used in icon
-----------------

Module icon was created by Alejandro Santana and includes some icons from
Font Awesome by Dave Gandy - http://fontawesome.io
which is under SIL OFL 1.1 ( http://scripts.sil.org/OFL ) license,
allowing derivative works.

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
