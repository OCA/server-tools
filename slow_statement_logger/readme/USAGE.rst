Add ``slow_statement_logger`` to Odoo's ``--load`` command line option, or to the
``server_wide_modules`` configuration file entry.

Add a ``log_min_duration_statement`` entry in the ``options`` section of your
Odoo configuration file. Statements running at least this number of
milliseconds will be logged with a *debug* level in the
``odoo.addons.slow_statement_logger`` logger. ``0`` means all statements will be
logged. ``-1`` disables this logging. You can also set an environment variable
``ODOO_LOG_MIN_DURATION_STATEMENT`` which will have priority over the
configuration file entry.

Add ``odoo.addons.slow_statement_logger:DEBUG`` in your ``log_handler``
configuration file entry or ``--log-handler`` command line option.
