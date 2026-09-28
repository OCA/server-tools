You don't need to install this module in the database(s) to enable it.

But you need to load it server-wide:

* By starting Odoo with ``--load=base,web,base_cron_reconnect``

* Or by updating its configuration file:

.. code-block:: ini

  [options]
  (...)
  server_wide_modules = base,web,base_cron_reconnect

This is required, not optional: the patch has to be in place before
``cron_spawn()`` runs, and ``load_server_wide_modules()`` is the first
statement of ``odoo.service.server.start()`` - guaranteed to run before
any database registry is loaded. A database-installed addon has no such
guarantee (its Python may not even be imported until the first request,
notably with a dynamic ``dbfilter`` setup and no fixed ``--database``),
i.e. potentially after the cron threads already resolved the unpatched
method. Installing this module from the Apps list is harmless (it has
no models or data) but does **not**, by itself, activate anything.

To verify the patch is active, check the server log at startup for::

  base_cron_reconnect: patched ThreadedServer.cron_thread to survive a
  lost database connection (retry interval: 60s).

If that line is missing, look for ``Failed to load server-wide module``
instead - ``load_server_wide_modules()`` silently swallows exceptions
from a module's ``post_load`` hook and boots unpatched.
