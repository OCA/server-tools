# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0-or-later (https://www.gnu.org/licenses/agpl).
{
    "name": "Import Match by Fields",
    "summary": (
        "Update existing records on import by matching any stored field(s), "
        "without requiring the External ID."
    ),
    "version": "18.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["carlosdauden"],
    "license": "AGPL-3",
    "depends": ["base_import"],
    "data": [
        "security/ir.model.access.csv",
        "views/base_import_match_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
}
