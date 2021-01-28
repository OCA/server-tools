# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "test_jsonify_stored",
    "category": "Uncategorized",
    "summary": "Test Jsonify Stored",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://acsone.eu",
    "depends": ["jsonify_stored"],
    "application": False,
    "data": ["security/ir.model.access.csv", "data/export.xml"],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
}
