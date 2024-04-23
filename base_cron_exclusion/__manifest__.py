# Copyright 2017-21 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Base Cron Exclusion",
    "summary": "Allow you to select scheduled actions that should not run "
    "simultaneously.",
    "version": "17.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["LoisRForgeFlow", "ChrisOForgeFlow"],
    "development_status": "Production/Stable",
    "website": "https://github.com/OCA/server-tools",
    "category": "Tools",
    "depends": ["base"],
    "data": ["views/ir_cron_view.xml"],
    "license": "LGPL-3",
    "installable": True,
}
