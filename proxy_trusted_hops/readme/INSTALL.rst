You don't have to install this module in a database. Add it to the
``server_wide_modules`` list so it is active as soon as the server starts:

.. code-block:: cfg

    server_wide_modules = base,web,proxy_trusted_hops
