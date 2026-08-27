There is nothing to click: once loaded server-wide, the module works
silently in the background.

Odoo's own cron only logs its start at DEBUG (invisible by default) and
nothing at all on a graceful stop. This module logs the lifecycle at
INFO instead, matching the style of ``queue_job``'s jobrunner
("starting"/"stopped")::

  INFO ... base_cron_reconnect: patched ThreadedServer.cron_thread to
  survive a lost database connection (retry interval: 60s).
  INFO ... cron0 starting

What a recovery looks like in the log::

  WARNING ... cron0 died, most likely due to a lost database connection;
  restarting it in 60s.
  Traceback (most recent call last):
  ...
  INFO ... cron0 restarting now.

And on a clean server shutdown while a retry is pending::

  INFO ... cron0 stopped gracefully

Recommended: alert on ``WARNING``-level records from the
``odoo.addons.base_cron_reconnect.hooks`` logger - the point of this
module is as much observability as recovery. A cron thread crashing at
all usually means something worth investigating (a database restart, a
network issue, connection pool exhaustion); this module's own record is
deliberately a ``WARNING``, not an ``ERROR``, since the underlying
disconnect itself is already logged (e.g. by ``odoo.sql_db``) and this
one just confirms the thread is recovering on its own.

No ``WARNING`` is logged on a normal, clean server restart - the module
tracks the shutdown signal and stays quiet in that case, so the alert
stays low-noise.

To verify on a test instance: restart the PostgreSQL server (or its
container) while Odoo is running in threaded mode with this module
loaded, and watch the log for the ``WARNING`` above followed by
``cron%d restarting now.`` and normal cron polling resuming.
