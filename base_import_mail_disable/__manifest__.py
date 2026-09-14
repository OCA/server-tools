# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Base Import Mail Disable",
    "summary": "Disables sending of emails and notifications during data imports "
    "to avoid flooding",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "Heliconia Solutions Pvt. Ltd., Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "base_import",
        "mail",
    ],
    "data": [],
    "maintainers": ["Bhavesh Heliconia"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
