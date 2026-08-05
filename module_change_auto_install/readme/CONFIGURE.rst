* Edit your ``odoo.cfg`` configuration file:

* Add the module ``module_change_auto_install`` in the ``server_wide_modules`` list.

* (optional) Add a new entry ``modules_auto_install_disabled`` to mark
  a list of modules as NOT auto installable.

* (optional) Add a new entry ``modules_auto_install_enabled`` to mark
  a list of modules as auto installable. This feature can be usefull for companies
  that are hosting a lot of Odoo instances for many customers, and want some modules
  to be always installed.

**Typical Settings**

.. code-block:: shell

    server_wide_modules = web,module_change_auto_install

    modules_auto_install_disabled = partner_autocomplete,iap,mail_bot,account_edi,account_edi_facturx,account_edi_ubl

    modules_auto_install_enabled = web_responsive,web_no_bubble,base_technical_features,disable_odoo_online,account_menu

Run your instance and check logs. Modules that has been altered should be present in your log, at the load of your instance:

.. code-block:: shell

    INFO db_name odoo.addons.module_change_auto_install.patch: Module 'iap' has been marked as not auto installable.
    INFO db_name odoo.addons.module_change_auto_install.patch: Module 'mail_bot' has been marked as not auto installable.
    INFO db_name odoo.addons.module_change_auto_install.patch: Module 'partner_autocomplete' has been marked as not auto installable.
    INFO db_name odoo.addons.module_change_auto_install.patch: Module 'account_edi' has been marked as not auto installable.
    INFO db_name odoo.addons.module_change_auto_install.patch: Module 'account_edi_facturx' has been marked as not auto installable.
    INFO db_name odoo.addons.module_change_auto_install.patch: Module 'account_edi_ubl' has been marked as not auto installable.
    INFO db_name odoo.modules.loading: 42 modules loaded in 0.32s, 0 queries (+0 extra)
