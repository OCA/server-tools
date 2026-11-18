Once installed, an administrator who tries to install, upgrade or uninstall
a module from the web interface gets an error such as:

> Module installation is disabled on this database. The following modules
> were not installed: pos_restaurant. Ask your Odoo partner to add them to
> the project and deploy them.

To install a module, add it to the code (for example to the `depends` of the
project's bundle module) and deploy it with `odoo -u` or
`click-odoo-update`.

In Settings, modules are installed when the settings are saved. When the
install is refused, the whole save is rolled back, including the other
settings changed at the same time.
