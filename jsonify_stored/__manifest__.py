# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "jsonify_stored",
    "category": "Uncategorized",
    "summary": "Jsonify Stored",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://acsone.eu",
    "depends": ["base_jsonify", "base_sparse_field", "queue_job"],
    "application": False,
    "data": ["data/cron.xml"],
    "demo": [],
}
