# Copyright 2026 Ryan Cole (https://www.ryanc.me)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "OpenTelemetry",
    "summary": "Fully featured OpenTelemetry integration for Odoo",
    "author": "Ryan Cole, Odoo Community Association (OCA)",
    "maintainers": ["ryanc-me"],
    "category": "Technical",
    "website": "https://github.com/OCA/server-tools",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "installable": True,
    "depends": ["web"],
    "post_load": "post_load",
    "sequence": 999,
}
