Access Rights
-------------

The changesets rules must be edited by users with the group ``Changesets
Configuration``. The changesets can be applied or canceled only by users
with the group ``Changesets Validations``

Changesets Rules
----------------

The changesets rules can be configured in ``Configuration >
Record Changesets > Fields Rules``.

* Configuration of rules

  .. image:: base_changeset/static/src/img/rules.png

For each record field, an action can be defined:

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
* Monetary
* Boolean
* Many2one

Rules can be global (no source model) or configured by source model.
Rules by source model have the priority. If a field is not configured
for the source model, it will use the global rule (if existing).

If a field has no rule, it is written to the record without changeset.
