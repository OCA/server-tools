This module makes it possible to use
[PgBouncer](https://pgbouncer.github.io/) as a connection pooler for
odoo.

## Why isn't odoo's connection pooling good enough?

Odoo's builtin connection pooling works at process level: each Odoo
process has its own
[ConnectionPool](https://github.com/odoo/odoo/blob/12.0/odoo/sql_db.py#L525),
limited to `db_maxconn`.

It does the job of re-using open connections available in the pool. But
it never closes these connections, [unless reaching
db_maxconn](https://github.com/odoo/odoo/blob/12.0/odoo/sql_db.py#L593).

In practice, we observe that each odoo worker will end up with up to 3
open connection in its pool. With 10 http workers, that's up to 30
connection continuously open just for one single instance.

## Here comes PgBouncer

PgBouncer will help to limit this number of open connections, by sharing
a pool of connections at the instance level, between all workers. Odoo
workers will still have up to 3 open connections, but these will be
connections to PgBouncer, that on its side will close unnecessary
connections to pg.

This has proven to help performances on Odoo deployments with multiple
instances.

It allows you to define how resources should be shared, according to
your priorities, e.g. :

- key odoo instance on host A can open up to 30 connections
- while odoo instance on host B, dedicated to reports, can open up to 10
  connections only

And most importantly, it helps you to ensure that `max_connections` will
never be reached on pg server side.

## Why is this module needed?

When configuring PgBouncer, you can choose between 2 transaction pooling
modes:

- pool_mode = session
- pool_mode = transaction

If we choose pool_mode = session, then one server connection will be
tied to a given odoo process until its death, which is exactly what
we're trying to change. Thus, to release the server connection once the
transaction is complete, we use pool_mode = transaction.

This works fine, except for Odoo's longpolling features that relies on
the
[LISTEN/NOTIFY](https://www.postgresql.org/docs/9.6/static/sql-notify.html)
mechanism from pg, which is [not
compatible](https://wiki.postgresql.org/wiki/PgBouncer) with that mode.

To be more precise, NOTIFY statements are properly transfered by
PgBouncer in that mode; only the LISTEN statement isn't (because it
needs to keep the server connection open).

So for the unique "listening" connection per instance that requires this
statement
([here](https://github.com/odoo/odoo/blob/12.0/addons/bus/models/bus.py#L166)),
we need odoo to connect directly to the pg server, bypassing PgBouncer.

That's what this module implements, by overriding the relevant method of
the
[Dispatcher](https://github.com/odoo/odoo/blob/12.0/addons/bus/models/bus.py#L105).
