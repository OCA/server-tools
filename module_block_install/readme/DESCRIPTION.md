This module blocks installing, upgrading and uninstalling modules from the
web interface and from RPC, including for administrators.

Odoo already restricts module operations to administrators. But on a
production database, the customer usually has an administrator account, and
an install from the web interface:

- runs on the live database, in the web worker that received the click, and
  takes locks on the tables it changes, which can freeze Odoo for every user;
- installs a module that has not been assessed and tested on staging;
- is not in the code, so staging, a new environment or a restore built from
  the repository will not have it.

The rule is simple: a module operation is refused when it runs **inside an
HTTP request** (web client, `/json/2`, XML-RPC, JSON-RPC), whoever the user is, unless
the request comes from an allowed IP address. Outside an HTTP request
(`odoo -i/-u`, `click-odoo-update`, `odoo shell`, server-side scripts), it
goes through. A module added to the code as a dependency of an upgraded
module is still installed at deploy time.

The guarded entry points are:

- `button_install`, `button_immediate_install`;
- `button_upgrade`, `button_immediate_upgrade`;
- `button_uninstall`, `button_immediate_uninstall`,
  `button_uninstall_wizard`, `module_uninstall`;
- "Apply Scheduled Upgrades" (`base.module.upgrade`).

This covers the Apps menu, the `module_*` checkboxes in Settings, and the
buttons of other addons that install modules (localizations installed when
setting a company's country, payment providers, the website configurator,
Point of Sale options, ...). "Update Apps List" stays allowed: it installs
nothing.

Each refused call raises an error telling the user which modules were not
processed, and is logged at `WARNING` level with the method, the modules,
the user and the IP address.
