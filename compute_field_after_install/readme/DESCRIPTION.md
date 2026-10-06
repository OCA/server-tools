Computed field computation can be a really long process when installing
a module and can block the migration process for a long time.

This module gives the possibility to defer the field computation after
the installation.

:warning: Use with caution :warning:

Not all computed fields can be deferred without risking the generation of
corrupted data. E.g. the total amount of an invoice, if differed, could lead
to wrong data computation in other stored fields that depend on it. That's why
this module should never be used in a database migration process such as
OpenUpgrade, where computed fields have to be triggered by the framework
as expected.
