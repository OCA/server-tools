This module extends the functionality of records. It allows to create
changesets that must be validated when a record is modified instead of direct
modifications. Rules allow to configure which field must be validated.

What is a changeset
-------------------

A changeset is a list of changes made on a record.

Some of the changes may be 'Pending', some 'Accepted' or 'Rejected' according
to the changeset rules.  The 'Pending' changes require an interaction by the
approver user: only when that change is approved, its value is written on
the record.
