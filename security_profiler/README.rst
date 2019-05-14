.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3

=================
Security Profiler
=================

This module lets log the security workflow of a specific user. Specifically,
each time the profiled user access to a model view or clicks on a menu,
that access or menu is logged.

Then, from this logged workflow, you can export a security proposal for that user.
This proposal will be a group, and access rights, actions and menu views for that group.

Installation
============

To install this module, simply follow the standard install process.

Usage
=====

To use this module, you need to:

#. Go to `Settings` -> `Technical` -> `Security` -> `Users Profiler Sessions`
#. Create a session filling the form. If `Log` if checked, the user will be logged.
   Put in `Implied Groups` only the basic groups that the user always will have.
#. Click on `Print` -> `Security Proposal Role Group` to obtain a security proposal
   based on the logged data.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/144/11.0

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

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------

* Miquel Raïch <miquel.raich@eficent.com>

Do not contact contributors directly about support or help with technical issues.

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
