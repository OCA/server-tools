You need to install this module in the database(s) to enable it.

And you also need to load it server-wide:

* By starting Odoo with ``--load=web,bus_alt_connection``

* Or by updating its configuration file:

.. code-block:: ini

  [options]
  (...)
  server_wide_modules = web,bus_alt_connection
