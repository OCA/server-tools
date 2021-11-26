You need to load this module server-wide:

* By starting Odoo with ``--load=web,base_deterministic_session_gc``

* Or by updating its configuration file:

.. code-block:: ini

  [options]
  (...)
  server_wide_modules = web,base_deterministic_session_gc

You also need to install it in your database
if you want to use the provided deterministic approach.
