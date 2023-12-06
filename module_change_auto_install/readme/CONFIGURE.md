- Edit your `odoo.cfg` configuration file:
- Add the module `module_change_auto_install` in the
  `server_wide_modules` list.
- (optional) Add a new entry `modules_auto_install_disabled` to mark a
  list of modules as NOT auto installable.
- (optional) Add a new entry `modules_auto_install_enabled` to mark a
  list of modules as auto installable. This feature can be usefull for
  companies that are hosting a lot of Odoo instances for many customers,
  and want some modules to be always installed.

**Typical Settings**

``` shell
server_wide_modules = web,module_change_auto_install

modules_auto_install_disabled =
    partner_autocomplete,
    iap,
    mail_bot

modules_auto_install_enabled =
    web_responsive:web,
    base_technical_features,
    disable_odoo_online,
    account_usability
```

Run your instance and check logs. Modules that has been altered should
be present in your log, at the load of your instance:

``` shell
INFO db_name odoo.addons.module_change_auto_install.patch: Module 'iap' has been marked as NOT auto installable.
INFO db_name odoo.addons.module_change_auto_install.patch: Module 'mail_bot' has been marked as NOT auto installable.
INFO db_name odoo.addons.module_change_auto_install.patch: Module 'partner_autocomplete' has been marked as NOT auto installable.
INFO db_name odoo.modules.loading: 42 modules loaded in 0.32s, 0 queries (+0 extra)
```

**Advanced Configuration Possibilities**

if your `odoo.cfg` file contains the following configuration:

``` shell
modules_auto_install_enabled =
    account_usability,
    web_responsive:web,
    base_technical_features:,
    point_of_sale:sale/purchase
```

The behaviour will be the following:

- `account_usability` module will be installed as soon as all the
  default dependencies are installed. (here `account`)
- `web_responsive` module will be installed as soon as `web` is
  installed. (Althought `web_responsive` depends on `web` and `mail`)
- `base_technical_features` will be ALWAYS installed
- `point_of_sale` module will be installed as soon as `sale` and
  `purchase` module are installed.
