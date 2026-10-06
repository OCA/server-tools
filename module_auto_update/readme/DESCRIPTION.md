This addon provides mechanisms to compute sha1 hashes of installed
addons, and save them in the database. It also provides a method that
exploits these mechanisms to update a database by upgrading only the
modules for which the hash has changed since the last successful
upgrade.

As an alternative to this module
[click-odoo-update](https://github.com/acsone/click-odoo-contrib) can
also be integrated in your non-Odoo maintenance tools instead.

This module gives Odoo the ability to upgrade a module automatically when its version
number is bumped, similar to how Odoo.sh works. This feature is very useful in Docker
deployments (doubly-so for docker-in-cloud), where upgrading modules via the
command-line can be difficult or impossible.

In particular, this module is handy when adding new fields to `res.users` or
`res.company`, which will often cause the Odoo UI to break until the module is upgraded.
