This module is not installable, to use this module, you need to:

1. Run odoo with this module as a server module:

.. code-block:: shell

  odoo -d DATABASE_NAME -i MODULE_TO_MIGRATE --load=base,web,views_migration_17 --stop-after-init

2. If successful, the modifications will be applied to the source code of your module. Alternatively, you can set the environment variable `VIEWS_MIGRATION_17_OUTPUT_DIR` to specify a different output directory for the modified views. Ensure that the user running the Odoo process has the appropriate permissions for the specified path.

.. code-block:: shell

  export VIEWS_MIGRATION_17_OUTPUT_DIR=/path/to/output/directory

Example in a [doodba-copier-template](https://github.com/Tecnativa/doodba-copier-template) project:

.. code-block:: shell

  docker compose run -e VIEWS_MIGRATION_17_OUTPUT_DIR=/opt/odoo/auto/migrated_views -u odoo --rm odoo odoo -d devel -i $modules --load=base,web,views_migration_17 --stop-after-init
