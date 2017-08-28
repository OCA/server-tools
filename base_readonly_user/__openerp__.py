# -*- coding: utf-8 -*-
# Copyright 2017 Lorenzo Battistini - Agile Business Group
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl).

{
    "name": "Read only user",
    "version": "7.0.1.0.0",
    "description": """

.. image:: https://img.shields.io/badge/licence-GPL--3-blue.svg
   :target: http://www.gnu.org/licenses/gpl
   :alt: License: GPL-3

==============
Read only user
==============

This module allows to configure a user as 'readonly':
the user will only be able to read data, without modifying

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: Icon

Contributors
------------

* Lorenzo Battistini <lorenzo.battistini@agilebg.com>

Do not contact contributors directly about support or
help with technical issues.

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
""",
    "website": "https://odoo-community.org/",
    "author": "Agile Business Group, Odoo Community Association (OCA)",
    "license": "GPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
    ],
    "data": [
        "views/user_view.xml",
    ],
    "demo": [
    ],
}
