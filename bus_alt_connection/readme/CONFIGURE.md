You need to define how to connect directly to the database:

- Either by defining environment variables:

  > - `IMDISPATCHER_DB_HOST=db-01`
  > - `IMDISPATCHER_DB_PORT=5432`

- Or in Odoo's configuration file:

``` ini
[options]
(...)
imdispatcher_db_host = db-01
imdispatcher_db_port = 5432
```

The cron LISTEN connections use the same settings by default. If you
need a different host/port for them, you can override it:

- Either by defining environment variables:

  > - `ODOO_CRON_DB_HOST=db-01`
  > - `ODOO_CRON_DB_PORT=5432`

- Or in Odoo's configuration file:

``` ini
[options]
(...)
cron_db_host = db-01
cron_db_port = 5432
```
