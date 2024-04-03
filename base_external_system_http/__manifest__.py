# Copyright 2023-2024 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "External System HTTP",
    "version": "16.0.1.0.0",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "maintainers": ["NL66278"],
    "license": "AGPL-3",
    "category": "Base",
    "website": "https://github.com/OCA/server-tools",
    "summary": "HTTP Connector for External Systems",
    "depends": ["base_external_system"],
    "data": [
        "demo/external_system_demo.xml",
        "demo/external_system_endpoint_demo.xml",
        "security/ir.model.access.csv",
        "views/external_system.xml",
    ],
    "installable": True,
    "application": False,
}
