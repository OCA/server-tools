.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================
Security Safe Password
======================

This module adds some constraints below for user password
     - at least 7 characters. The number of characters is set in a system parameter.
     - at least one letter in lower case
     - at least one letter in upper case
     - at least one number
There is also an configure parameter to check the password 
strength with the python package "cracklib".

Installation
============

To install this module, you need to:

* Install the python package "cracklib" first
	- sudo apt-get install libcrack2-dev
	- pip install cracklib==2.9.3


Usage
=====

To use this module, you need to:

* Go to Settings / Technical / Parameter / System Parameters, then update
	- length_password: to specify the number of characters in user password
	- password_check_cracklib: to enable the check from cracklib

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/{repo_id}/{branch}

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "8.0" for example


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
server-tools/issues/new?body=module:%20
{module_name}%0Aversion:%20
{branch}%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Trobz <contact@trobz.com>

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