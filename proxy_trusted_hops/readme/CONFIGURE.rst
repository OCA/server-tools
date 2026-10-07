Set the number of reverse proxies in front of Odoo, either with the
``ODOO_TRUSTED_PROXIES`` environment variable or in the Odoo configuration
file:

.. code-block:: cfg

    proxy_mode = True
    trusted_proxies = 2

The environment variable takes precedence over the configuration file.

As in Odoo itself, the header is only used when ``proxy_mode`` is enabled and
the request contains an ``X-Forwarded-Host`` header.

With ``trusted_proxies = N``, Odoo uses the N-th address from the end of the
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
