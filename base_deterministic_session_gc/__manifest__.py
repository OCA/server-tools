# Copyright 2019 Trobz <https://trobz.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Deterministic Session GC",
    "summary": "Provide a deterministic session garbage collection"
    " instead of the default random one",
    "version": "13.0.1.0.0",
    "author": "Trobz,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "category": "Extra Tools",
    "license": "AGPL-3",
    "data": ["data/ir_cron_data.xml"],
    "depends": ["mail"],
    "installable": True,
    "auto_install": False,
}
