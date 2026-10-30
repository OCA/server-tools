# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Base Sequence Template",
    "summary": "Create a sequence template that can generate sequences for companies",
    "category": "Tools",
    "version": "18.0.1.0.0",
    "website": "https://github.com/OCA/server-tools",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["base_setup"],
    "data": [
        "views/ir_sequence_template_views.xml",
        "wizard/generate_company_sequences.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "auto_install": False,
}
