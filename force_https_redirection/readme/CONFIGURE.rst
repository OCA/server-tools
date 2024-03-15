To enable HTTPS redirection needs to set this module
in the `server_wide_modules` list.

This is required to properly load the middleware at the very beginning.
of the module. So even the module is not
installed on any database the middleware will be loaded.
