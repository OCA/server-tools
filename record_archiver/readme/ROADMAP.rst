The default behavior is to archive all records having a ``write_date`` <
lifespan and with a state being ``done`` or ``cancel``. If these rules
need to be modified for a model (e.g. change the states to archive), the
hook ``RecordLifespan._archive_domain`` can be extended.
