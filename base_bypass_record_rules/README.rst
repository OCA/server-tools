.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===================
Bypass Record Rules
===================

This module allows to bypass record rule permissions on relational fields
visibility.

For example in a multi-company environment it allows to see the records of
company B for a user of company A, even if the user has no visibility on
these records (i.e. B is not an allowed company).

Installation
============

No specific requirements.

Configuration
=============

Check the flag 'Can be bypassed' in the record rule form.
In a model view, edit the context property for the desired field: add the
'can_bypass_record_rules' key set to a list of groups that should be able to
bypass the record rule permissions.

If the user is in any of the listed groups, he will be able to bypass the
flagged record rule.

For example:

<field name="my_field"
   context="{'can_bypass_record_rules': ['base.group_user']}">

Usage
=====

No specific requirements.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/10.0

Known issues / Roadmap
======================

No known issues.

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

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Roberto Onnis <roberto.onnis@innoviu.com>
* Simone Rubino <simone.rubino@agilebg.com>

Do not contact contributors directly about support or help with technical issues.

Funders
-------

The development of this module has been financially supported by:

* Agile Business Group Sagl

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
