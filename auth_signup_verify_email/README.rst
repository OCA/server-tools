.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================
Verify email at signup
======================

This module extends the functionality of public sign up, and forces users to
provide a valid email address.

To achieve this requirement, the user does not need to provide a password at
sign up, but when logging in later for the first time.

Installation
============

* Install validate_email_ with ``pip install validate_email`` or equivalent.

Configuration
=============

To configure this module, you need to:

* `Properly configure your outgoing email server(s)
  <https://www.odoo.com/es_ES/forum/help-1/question/how-to-configure-email-gateway-282#answer_290>`_.
* Go to *Settings > Configuration > General Settings* and enable *Allow
  external users to sign up*.

Usage
=====

To use this module, you need to:

* Log out.
* `Sign up </web/signup>`_ with a valid email.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/ website/issues>`_.

In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and
welcomed feedback `here <https://github.com/OCA/
website/issues/new?body=module:%20 auth_signup_verify_email%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Icon
----

* https://openclipart.org/detail/3040/thumbtack-note-email
* https://openclipart.org/detail/202732/check-mark

Contributors
------------

* Rafael Blasco <rafaelbn@antiun.com>
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

To contribute to this module, please visit http://odoo-community.org.

.. _validate_email: https://pypi.python.org/pypi/validate_email
