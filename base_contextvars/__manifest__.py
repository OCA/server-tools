# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Contextvars Patch",
    "summary": """
        Patch Odoo threadlocals to use contextvars instead.""",
    "version": "14.0.1.0.3",
    "license": "LGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["sbidoul"],
    "website": "https://github.com/OCA/server-tools",
    "external_dependencies": {"python": ["contextvars"]},
}
