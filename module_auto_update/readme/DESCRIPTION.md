This addon provides mechanisms to compute sha1 hashes of installed
addons, and save them in the database. It also provides a method that
exploits these mechanisms to update a database by upgrading only the
modules for which the hash has changed since the last successful
upgrade.

As an alternative to this module
[click-odoo-update](https://github.com/acsone/click-odoo-contrib) can
also be integrated in your non-Odoo maintenance tools instead.
