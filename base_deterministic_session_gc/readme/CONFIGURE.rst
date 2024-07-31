You can change the session expiry delay in the Odoo configuration file:

.. code-block:: ini

  [options]
  (...)
  ; 1 day = 60*60*24 seconds
  session_expiry_delay = 86400

Default value is 7 days.
