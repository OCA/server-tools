# Copyright 2026 (APSL-Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Base Autocomplete Templates",
    "summary": "Generic JSON-based templates to autocomplete any wizard/form.",
    "version": "17.0.1.0.0",
    "author": "APSL/Nagarro, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/server-tools",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/data_autocomplete_template_views.xml",
        "wizards/data_autocomplete_create_wizard.xml",
    ],
    "maintainers": ["BernatObrador"],
    "installable": True,
    "application": False,
}
