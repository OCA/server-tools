# Copyright 2024 Camptocamp (https://www.camptocamp.com).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

{
    "name": "Force Record No-update",
    "summary": "Manually force noupdate=True on models",
    "author": "Camtocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "category": "Hidden",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["base"],
    "data": ["views/ir_model.xml"],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
