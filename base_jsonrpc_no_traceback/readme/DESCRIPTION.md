This module prevents Odoo from leaking Python tracebacks through JSON-RPC
error responses.

By default, Odoo includes the full Python traceback in the `debug` key of
every JSON-RPC error response, even when the server does not run in developer
mode. This exposes internal file paths, module names and versions to any
caller able to trigger an error.

Once installed, this module leaves the `debug` key empty unless the server
runs in developer mode (`--dev`).
