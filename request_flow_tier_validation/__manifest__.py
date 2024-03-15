# Copyright 2021 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Request Flow Tier Validation",
    "summary": "Extends the functionality of Requests to "
    "support a tier validation process.",
    "version": "14.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["request_flow", "base_tier_validation"],
    "data": [
        "security/request_security.xml",
        "views/request_views.xml",
        "views/request_category_views.xml",
    ],
    "application": False,
    "installable": True,
    "uninstall_hook": "uninstall_hook",
}
