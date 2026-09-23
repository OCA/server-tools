Allow configuration of the number of trusted proxies for accurate Client IP detection.

By default, Odoo’s http.ProxyFix is hardcoded to trust exactly one proxy. In this configuration, Odoo assumes the rightmost IP in the X-Forwarded-For header is the immediate proxy and the one preceding it is the Client IP.

However, in complex network topologies, the X-Forwarded-For list contains multiple hops. If Odoo only trusts one hop when two or more exist, it will incorrectly identify one of your internal proxies as the "Client IP".

This module allows you to configure the number of trusted proxies via an environment variable, enabling Odoo to "peel back" the correct number of layers to find the authentic Client IP.