Please keep in mind that the standard odoo dbfilter configuration is
still applied before looking at the regular expression in the header.

- For nginx, use:

  `proxy_set_header X-Odoo-dbfilter [your filter regex];`

- For caddy, use:

  `proxy_header X-Odoo-dbfilter [your filter regex]`

- For Apache, use:

  `RequestHeader set X-Odoo-dbfilter [your filter regex]`

And make sure that proxy mode is enabled in Odoo's configuration file:

`proxy_mode = True`
