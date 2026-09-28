When Odoo runs with ``workers = 0`` (threaded mode), scheduled actions are
executed by a small number of long-lived ``cron`` threads spawned once at
server startup (``ThreadedServer.cron_spawn()``).

If the database connection those threads hold is lost - for example
because PostgreSQL restarts or briefly drops connections during
maintenance or a failover - the affected thread crashes with an
unhandled ``psycopg2.OperationalError`` and is never respawned. Every
scheduled action on that Odoo process then silently stops running,
forever, until someone notices and restarts the whole server. HTTP
requests are unaffected (they borrow a fresh connection per request), so
nothing in the application itself signals that anything is wrong.

This module patches ``ThreadedServer.cron_thread`` at server startup
(``post_load``) so that a crashed cron thread is logged and retried
after a short delay instead of staying dead, mirroring the retry
pattern Odoo's own ``bus`` module already uses for its long-lived
``LISTEN``/``NOTIFY`` connection (``bus.models.bus.ImDispatch.run()``).
It also logs its own start/stop at ``INFO`` - Odoo's native cron only
logs those at ``DEBUG`` or not at all. See ``USAGE.rst`` for the exact
log lines and recommended alerting.

This only applies to threaded mode. In prefork mode (``workers`` > 0),
Odoo's own ``PreforkServer`` already respawns a crashed ``WorkerCron``
process on its own, so this module has no effect there.

Related upstream reports - not overlooked, but core has taken a
position that automatic recovery isn't in scope for
``ThreadedServer``:

* https://github.com/odoo/odoo/issues/15666 (2017, fixed for the
  pre-``LISTEN``/``NOTIFY`` code of the time; the current call site is
  unguarded again)
* https://github.com/odoo/odoo/issues/88984 - closed **Won't fix**,
  with an explicit rationale that DB availability is a system
  administrator's responsibility in threaded mode
* https://github.com/odoo/odoo/issues/184421 (open)
* https://github.com/odoo/odoo/issues/215164 (open)
