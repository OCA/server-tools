This module should be added to your addons directory just like any other module.
You should then add the module to your `server_wide_modules`, e.g.:

```ini
# odoo-server.conf

[options]
# ...
server_wide_modules = base,web,otel
```

You will also need to install the Python dependencies via pip:

```shell
pip3 install -r /path/to/otel/requirements.txt
```
