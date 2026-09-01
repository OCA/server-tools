You need to define how to connect directly to the database:

* Either by defining environment variables:

    - ``ODOO_IMDISPATCHER_DB_HOST=db-01``
    - ``ODOO_IMDISPATCHER_DB_PORT=5432``

* Or in Odoo's configuration file:

.. code-block:: ini

  [options]
  (...)
  imdispatcher_db_host = db-01
  imdispatcher_db_port = 5432
