Both options are read from the server configuration file, never from the
database: an administrator can change system parameters from the web
interface, and that is the user being blocked.

They go in a `[module_block_install]` section of their own, not in
`[options]`: since 19.0, Odoo warns about every option of `[options]` it does
not know.

``` cfg
[module_block_install]
enabled = True
allowed_ips = 203.0.113.10,198.51.100.0/24
```

With `server_environment` installed, the section is read from its
configuration instead.

- `enabled`: blocking is on by default as soon as the module is
  installed. Set it to `False` on development and test environments.
- `allowed_ips` (optional, empty by default): a
  comma-separated list of IP addresses or networks (CIDR notation). Requests
  coming from these addresses are not blocked, for example to let the
  integrator install a module from the web interface during a planned
  intervention.

Behind a reverse proxy, Odoo only sees the client's real address when
`proxy_mode` is on and the proxy sends the `X-Forwarded-*` headers. Otherwise
every request carries the proxy's address: never allow that address, it
would let everyone through.

The `/xmlrpc`, `/xmlrpc/2` and `/jsonrpc` endpoints are only recognised as
HTTP requests once the module's code is loaded in the server process. A
worker loads it with the database's registry, which, on a server without
`dbfilter` and without `--database`, can happen during the first such call.
To close that gap, also load the module server-wide:

``` cfg
[options]
server_wide_modules = base,rpc,web,module_block_install
```
