# Copyright (C) 2026 XXP
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Base Module Quick Update",
    "version": "16.0.1.0.0",
    "summary": "Adds a quick upgrade for the selected module without "
    "cascading upgrades of modules that depend on it.",
    "author": "XXP, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "license": "AGPL-3",
    "category": "Technical Settings",
    "depends": [
        "base",
    ],
    "data": [
        "views/ir_module_views.xml",
    ],
    "installable": True,
    "application": False,
}
