By default every model in the registry is warmed up. On a large database that
costs a few seconds of boot time per worker, which is usually a good trade,
but it can be narrowed down.

To warm up only the models that matter, set the system parameter
``base_field_trigger_warmup.models`` to a comma separated list of model names::

    base_field_trigger_warmup.models = account.move,account.move.line

Model names that do not exist in the registry are ignored with a warning.
Setting the parameter to ``*`` or leaving it empty restores the default of
warming up everything.

To disable the warmup entirely without uninstalling the module, for instance on
a development machine or in a CI pipeline where boot time matters more than the
first request, export::

    ODOO_FIELD_TRIGGER_WARMUP=0

The warmup is always skipped while tests are running.
