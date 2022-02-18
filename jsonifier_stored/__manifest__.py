# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Jsonify Stored",
    "summary": "Store Jsonified data based on an ir.export",
    "version": "14.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://github.com/OCA/server-tools",
    "author": ("ACSONE SA/NV, " "Camptocamp SA, " "Odoo Community Association (OCA)"),
    "maintainers": ["mmequignon"],
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "depends": ["base_jsonify", "base_sparse_field", "queue_job"],
    "data": ["data/ir_cron.xml", "data/queue_job.xml"],
    "demo": ["demo/tests.xml"],
}
