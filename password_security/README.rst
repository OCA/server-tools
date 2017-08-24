.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

=================
Password Security
=================

This module allows admin to set company-level password security requirements
and enforces them on the user.

It contains features such as

* Password expiration days
* Password length requirement
* Password minimum number of lowercase letters
* Password minimum number of uppercase letters
* Password minimum number of numbers
* Password minimum number of special characters

Configuration
=============

# Navigate to company you would like to set requirements on
# Click the ``Password Policy`` page
# Set the policies to your liking.

Password complexity requirements will be enforced upon next password change for
any user in that company.


Settings & Defaults
-------------------

These are defined at the company level:

=====================  =======   ===================================================
 Name                  Default   Description                             
=====================  =======   ===================================================
 password_expiration   60        Days until passwords expire
 password_length       12        Minimum number of characters in password
 password_lower        True      Require lowercase letter in password
 password_upper        True      Require uppercase letters in password
 password_numeric      True      Require number in password
 password_special      True      Require special character in password
 password_history      30        Disallow reuse of this many previous passwords
 password_minimum      24        Amount of hours that must pass until another reset
=====================  =======   ===================================================

Usage
=====

Configure using above instructions for each company that should have password
security mandates.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
    :alt: Try me on Runbot
    :target: https://runbot.odoo-community.org/runbot/149/10.0

Known Issues / Roadmap
======================


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/LasLabs/odoo-base/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us to smash it by providing detailed and welcomed feedback.


Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* James Foster <jfoster@laslabs.com>
* Dave Lasley <dave@laslabs.com>
* Nguyen Duc Tam <nguyenductamlhp@gmail.com>

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
