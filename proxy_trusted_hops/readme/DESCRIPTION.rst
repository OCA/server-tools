When ``proxy_mode`` is enabled, Odoo takes the client address from the
``X-Forwarded-For`` header, but it only trusts one proxy: it always takes the
last address of the header. Behind more than one reverse proxy (for example a
cloud load balancer in front of an ingress controller), that address is one of
your own proxies, not the client.

This module lets you configure how many proxies Odoo trusts. Odoo then uses
the address added by your outermost proxy, which is the real client.

This affects every place that uses the client address, for example the access
log, the login log, the login cooldown after failed attempts, reCAPTCHA, and
website visitors.
