# Copyright 2017 LasLabs Inc.
# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Module Auto Update",
    "summary": "Automatically update Odoo modules",
    "version": "14.0.1.1.1",
    "category": "Extra Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "LasLabs, "
    "Juan José Scarafía, "
    "Tecnativa, "
    "ACSONE SA/NV, "
    "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "uninstall_hook": "uninstall_hook",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/module_auto_update_views.xml",
    ],
    "development_status": "Production/Stable",
}
