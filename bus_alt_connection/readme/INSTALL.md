You don't need to install this module in the database(s) to enable it.

But you need to load it server-wide:

- By starting Odoo with `--load=web,bus_alt_connection`
- Or by updating its configuration file:

``` ini
[options]
(...)
server_wide_modules = web,bus_alt_connection
```
