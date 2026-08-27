# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Base Cron Reconnect",
    "summary": "Restart threaded-mode cron workers that died on a lost "
    "database connection",
    "version": "16.0.1.0.0",
    "category": "Tools",
    "author": "Odoo Community Association (OCA)",
    "maintainers": [],
    "development_status": "Beta",
    "website": "https://github.com/OCA/server-tools",
    "license": "AGPL-3",
    "depends": ["base"],
    "post_load": "post_load",
    "installable": True,
}
