GrayLog2 GELF log handler
=========================

This module provides ability to send log messages to graylog2 server.

This module requires 'graypy' python package to be installed in system.

Note, that this addon should work event if it is not installed on database,
but present in Odoo addon_path.

Makes available aditional options in Odoo config file:
    gelf_enabled: bool      ; enable graylog2 logging
    gelf_host: string       ; required, graylog2 host
    gelf_port: integer      ; required, graylog2 port
    gelf_localname: string  ; optional, use specified hostname as source host


