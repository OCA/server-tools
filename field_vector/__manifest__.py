# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Field Vector",
    "summary": """New specialized field to store vector data""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "depends": ["base"],
    "maintainers": ["lmignon"],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
    "external_dependencies": {
        "python": ["numpy"],
    },
}
