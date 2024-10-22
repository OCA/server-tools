# Copyright 2023-2024 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Base External System - oauth systems",
    "summary": "Connect to external systems trough oauth authentication.",
    "version": "16.0.1.0.0",
    "category": "Base",
    "website": "https://github.com/OCA/server-tools",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "auth_oauth",
        "base_external_system_http",
    ],
    "data": [
        "views/external_system.xml",
        "views/auth_oauth_provider.xml",
    ],
}
