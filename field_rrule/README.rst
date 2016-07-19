.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

================
Repetition rules
================

This module was written to offer a field type that holds rrules according to RFC 2445.

Usage
=====

To use this module, you need to:

* depend on it
* say ``from openerp.addons.field_rrule import FieldRRule``
* use ``FieldRRule`` like any other field
* on forms, use ``widget="rrule"``
* have a look at `demo/res_partner.*`

Technically, this is a wrapper around serialized fields. The value always will be a subclass of dateutil's ``rruleset``. For technical reasons, this class overrides ``__iter__``, so if you need a proper ``rruleset``, call the value: ``my_browse_record.my_field_of_type_rrule()`` - this gives you a vanilla ``rruleset``.

If you want to pass a default, use the internal representation you'll find in the database - a list of dictionaries with the keyword arguments to be passed to rrule's constructor and a `type` field that for now can only be `rrule`: A context of ``{"default_rrule": [{"count": 1, "freq": 1, "type": "rrule", "interval": 1, "bymonthday": [1]}]}`` would give you a default for the field ``rrule`` which occurs one time at the first of the month.

In case you work with defaults and want to dumb down the UI a bit, use ``{'no_add_rule': true}``.

Further, as this is a serialized field, a value of `not set` will be represented in the database as ``'null'`` if the value was set and unset afterwards, or a database ``null`` if the value was never set - this is then also what you have to search for when you need records with your field unset.

Known issues / Roadmap
======================

* support the unimplemented features of rrules
* support rdates, exdates, exrules
* consider multiple widgets with different feature sets

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>  

Do not contact contributors directly about help with questions or problems concerning this addon, but use the `community mailing list <mailto:community@mail.odoo.com>`_ or the `appropriate specialized mailinglist <https://odoo-community.org/groups>`_ for help, and the bug tracker linked in `Bug Tracker`_ above for technical issues.

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
