You need to define how to connect directly to the database:

* Either by defining environment variables:

    - ``IMDISPATCHER_DB_HOST=db-01``
    - ``IMDISPATCHER_DB_PORT=5432``
    - ``IMDISPATCHER_DB_NAME=v12c``

* Or in Odoo's configuration file:

.. code-block:: ini

  [options]
  (...)
  imdispatcher_db_host = db-01
  imdispatcher_db_port = 5432
  imdispatcher_db_name = v12c
