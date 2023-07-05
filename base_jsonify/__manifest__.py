# Copyright 2017-2018 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Base Jsonify",
    "summary": "Base module that provide the jsonify method on all models",
    "version": "14.0.1.1.0",
    "category": "Uncategorized",
    "website": "https://github.com/OCA/server-tools",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/ir_exports_view.xml",
        "views/ir_exports_resolver_view.xml",
    ],
    "demo": [
        "demo/resolver_demo.xml",
        "demo/export_demo.xml",
        "demo/ir.exports.line.csv",
    ],
}
