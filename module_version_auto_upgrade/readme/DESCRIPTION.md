This module gives Odoo the ability to upgrade a module automatically when its version
number is bumped, similar to how Odoo.sh works. This feature is very useful in Docker
deployments (doubly-so for docker-in-cloud), where upgrading modules via the
command-line can be difficult or impossible.

In particular, this module is handy when adding new fields to `res.users` or
`res.company`, which will often cause the Odoo UI to break until the module is upgraded.