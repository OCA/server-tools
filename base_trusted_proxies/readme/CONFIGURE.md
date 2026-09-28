Adjust environment variable, for instance: `ODOO_TRUSTED_PROXIES=2`

Then load ``base_trusted_proxies`` as a server wide module:

- Using command line:
  - Start Odoo with `--load=web,base_trusted_proxies --proxy-mode`

- Using the Odoo configuration file:

``` ini
[options]
(...)
proxy_mode = True
server_wide_modules = web,base_trusted_proxies
```
