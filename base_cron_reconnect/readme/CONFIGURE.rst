The retry interval (in seconds) can optionally be configured. It defaults
to ``60`` (matching Odoo's own cron poll interval) if left unset or if an
invalid value is given.

Via the configuration file:

.. code-block:: ini

  [options]
  cron_reconnect_retry_interval = 30

Or via an environment variable, checked if the option above is not set:

.. code-block:: shell

  ODOO_CRON_RECONNECT_RETRY_INTERVAL=30

An invalid value (non-numeric, or below ``1``) falls back to the default
and logs a warning at startup rather than failing to boot.
