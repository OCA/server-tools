.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================
Partner Changesets
==================

This module extends the functionality of partners. It allows to create
changesets that must be validated when a partner is modified instead of direct
modifications. Rules allow to configure which field must be validated.

Configuration
=============

Access Rights
-------------

The changesets rules must be edited by users with the group ``Changesets
Configuration``. The changesets can be applied or canceled only by users
with the group ``Changesets Validations``

Changesets Rules
----------------

The changesets rules can be configured in ``Sales > Configuration >
Partner Changesets > Fields Rules``. For each partner field, an
action can be defined:

* Auto: the changes made on this field are always applied
* Validate: the changes made on this field must be manually confirmed by
  a 'Changesets User' user
* Never: the changes made on this field are always refused

In any case, all the changes made by the users are always applied
directly on the users, but a 'validated' changeset is created for the
history.

The supported fields are:

* Char
* Text
* Date
* Datetime
* Integer
* Float
* Boolean
* Many2one

Rules can be global (no source model) or configured by source model.
Rules by source model have the priority. If a field is not configured
for the source model, it will use the global rule (if existing).

If a field has no rule, it is written to the partner without changeset.

Usage
=====

General case
------------

The first step is to create the changeset rules, once that done, writes on
partners will be created as changesets.

Finding changesets
------------------

A menu lists all the changesets in ``Sales > Configuration > Partner
Changesets > Changesets``.

However, it is more convenient to access them directly from the
partners. Pending changesets can be accessed directly from the top right
of the partners' view.  A new filter on the partners shows the partners
having at least one pending changeset.

Handling changesets
-------------------

A changeset shows the list of the changes made on a partner. Some of the
changes may be 'Pending', some 'Accepted' or 'Rejected' according to the
changeset rules.  The only changes that need an action from the user are
'Pending' changes. When a change is accepted, the value is written on
the user.

The changes view shows the name of the partner's field, the Origin value
and the New value alongside the state of the change. By clicking on the
change in some cases a more detailed view is displayed, for instance,
links for relations can be clicked on.

A button on a changeset allows to apply or reject all the changes at
once.

Custom source rules in your addon
---------------------------------

Addons wanting to create changeset with their own rules should pass the
following keys in the context when they write on the partner:

* ``__changeset_rules_source_model``: name of the model which asks for
  the change
* ``__changeset_rules_source_id``: id of the record which asks for the
  change

Also, they should extend the selection in
``ChangesetFieldRule._domain_source_models`` to add their model (the
same that is passed in ``__changeset_rules_source_model``).

The source is used for the application of the rules, allowing to have a
different rule for a different source. It is also stored on the changeset for
information.

Screenshot:
-----------

* Configuration of rules

  .. image:: partner_changeset/static/src/img/rules.png

* Changeset waiting for validation

  .. image:: partner_changeset/static/src/img/changeset.png


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/134/9.0

Known issues / Roadmap
======================

* Only a subset of the type of fields is actually supported

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/partner-contact/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Denis Leemann <denis.leemann@camptocamp.com>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>

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
