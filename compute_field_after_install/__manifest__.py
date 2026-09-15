# Copyright 2025 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Compute field after install",
    "summary": "Compute computed fields after the install process",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "Akretion,Odoo Community Association (OCA)",
    "maintainers": ["sebastienbeau"],
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "base",
    ],
    "data": [
        "data/ir_cron.xml",
        "views/recompute_field_view.xml",
        "security/ir.model.access.csv",
    ],
}
