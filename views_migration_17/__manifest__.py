{
    "name": "Views Migration to v17",
    "version": "17.0.1.0.0",
    "author": "ODOO SA,ADHOC SA,Odoo Community Association (OCA)",
    "description": """
Patch modules views related to this change https://github.com/odoo/odoo/pull/104741
The script is taken from this comment (https://github.com/odoo/odoo/pull/104741#issuecomment-1794616832) on same PR
To run it:
1. Add module as server wide module.
2. Run odoo server installing or upgrading target module.

For eg: odoo -i upgrade_analysis -d upgrade_analysis --load=base,web,views_migration_17
""",
    "website": "https://github.com/OCA/server-tools",
    "license": "AGPL-3",
    "depends": [
        "base",
    ],
    "data": [],
    "installable": False,
    "auto_install": False,
    "application": False,
}
