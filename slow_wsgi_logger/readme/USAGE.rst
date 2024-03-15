Add a ``log_wsgi_request_min_duration`` entry in the ``options`` section of your
Odoo configuration file. WSGI requests running at least this number of
seconds will be logged. You can also set an environment variable
``ODOO_LOG_WSGI_REQUEST_MIN_DURATION`` which will have priority over the
configuration file entry. Default `30.0` seconds.

Add a ``log_wsgi_request_level`` entry in the ``options`` section of your
Odoo configuration file. WSGI requests logged will be raised with this level.
You can also set an environment variable ``ODOO_LOG_WSGI_REQUEST_LEVEL`` which
will have priority over the configuration file entry. Default `DEBUG` level.

with a *debug* level in the ``log_wsgi_request_level`` option. You can choose
to display those log adding ``odoo.addons.slow_wsgi_logger:DEBUG`` in your
``log_handler`` configuration file entry or ``--log-handler`` command line option.
