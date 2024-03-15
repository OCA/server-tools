# Copyright 2021 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Request Flow Exception",
    "summary": "Custom exceptions on request_flow",
    "version": "14.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "depends": ["request_flow", "base_exception"],
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "wizard/request_exception_confirm_view.xml",
        "views/request_view.xml",
    ],
    "installable": True,
    "maintainers": ["kittiu"],
}
