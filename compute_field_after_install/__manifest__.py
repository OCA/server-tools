# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Base compute field after install",
    "summary": "Computed field are computed after the install process",
    "version": "14.0.1.0.0",
    "category": "e-commerce",
    "website": "https://github.com/OCA/server-tools",
    "author": "Akretion,Odoo Community Association (OCA)",
    "maintainers": ["sebastienbeau"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": False,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
    ],
    "data": [
        "data/ir_cron.xml",
        "views/recompute_field_view.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [],
    "qweb": [],
}
