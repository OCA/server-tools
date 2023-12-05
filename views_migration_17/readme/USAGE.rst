This module is not installable, to use this module, you need to:

1. Run odoo with this module as a server module:

.. code-block:: shell

  odoo -d DATABASE_NAME -i MODULE_TO_MIGRATE --load=base,web,views_migration_17 --stop-after-init


2. If success the modifications will be in the source code of your module.

