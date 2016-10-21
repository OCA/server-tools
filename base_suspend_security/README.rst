.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3
Suspend security
=====================

This module was written to  allow you to call code with some `uid` while being sure no security checks (`ir.model.access` and `ir.rule`) are done. In this way, it's the same as `sudo()`, but the crucial difference is that the code still runs with the original user id. This can be important for inherited code that calls workflow functions, subscribes the current user to some object, etc.

Usually, you'll be in in the situation to want something like this if you inherit from a module you can't or don't want to change, and call `super()`.

Usage
=====

To use this module, you need to:

* depend on this module
* call `yourmodel.suspend_security().function_to_run()`, just the same as you would use `sudo()`

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

* the magic works by wrapping uid in a marker class, so if some code unwraps this in the calling tree, security checks will be reenabled

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20base_suspend_security%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>
* Laurent Mignon <laurent.mignon@acsone.eu>

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
