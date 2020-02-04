Changeset rules
---------------

The first step is to configure the changeset rules. Once that done, writes on
records will be created as changesets.

Handling changesets
-------------------

The list of all the changesets is in ``Configuration > Record
Changesets > Changesets``.

By default, only the pending changesets (waiting for validation) are shown.
Remove the "Pending" filter to show all the changesets.

* Changeset waiting for validation

  .. image:: base_changeset/static/src/img/changeset.png

The changes view shows the name of the record's field, the Origin value
and the New value alongside the state of the change. By clicking on the
change in some cases a more detailed view is displayed, for instance,
links for relations can be clicked on.

A button on a changeset allows to apply or reject all the changes at
once.

Handling single changes
-----------------------

Accessing the changesets gives the full overview of all the changes made.
However, it is more convenient to access the single changes directly from the
records. When there is a pending change for a field you get a badge with the
number of pending changes next to it like this:

* Badge with the number of pending changes

  .. image:: base_changeset/static/src/img/badge.png

When you click on it:

* Clicking the badge: red button to reject, green one to apply

  .. image:: base_changeset/static/src/img/badge_click.png

Click the red button to reject the change, click the green one to apply it.


Custom source rules in your addon
---------------------------------

Addons wanting to create changeset with their own rules should pass the
following keys in the context when they write on the record:

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
