# Copyright 2026 Pol Reig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Mass Module Updater",
    "summary": "Update multiple Odoo modules at once from a single wizard",
    "version": "18.0.1.0.0",
    "category": "Extra Tools",
    "license": "AGPL-3",
    "author": "Pol Reig, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/mass_module_updater_wizard_views.xml",
    ],
    "installable": True,
}
