# Copyright 2026 Akretion France (https://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Base JSON-RPC No Traceback",
    "summary": "Hide Python tracebacks in JSON-RPC error responses",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "category": "Hidden/Tools",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "depends": ["base"],
    "post_load": "post_load_hook",
    "installable": True,
}
