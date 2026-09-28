Set the number of reverse proxies in front of Odoo, either in the Odoo
configuration file:

.. code-block:: cfg

    proxy_mode = True
    proxy_trusted_hops = 2

or with the ``ODOO_PROXY_TRUSTED_HOPS`` environment variable. The value in the
configuration file takes precedence over the environment variable.

As in Odoo itself, the header is only used when ``proxy_mode`` is enabled and
the request contains an ``X-Forwarded-Host`` header.

With ``proxy_trusted_hops = N``, Odoo uses the N-th address from the end of the
``X-Forwarded-For`` header. If the header contains fewer addresses than that,
Odoo keeps the address of the connecting proxy.

**Security warning:** the client can send its own ``X-Forwarded-For`` header,
and proxies only add their entry to it. Never set a value higher than the
number of proxies that actually add an entry: otherwise the client decides
which address Odoo sees, and can for example get around the login cooldown.
Each proxy must add its entry to the header.

Check the server log at startup:

.. code-block:: shell

    INFO ? odoo.addons.proxy_trusted_hops.patch: Trusting 2 proxies for the X-Forwarded-For header.
