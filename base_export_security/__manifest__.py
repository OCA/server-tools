# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Export Security",
    "summary": "Security features for Odoo exports",
    "version": "10.0.1.0.0",
    "category": "Extra Tools",
    "website": "https://odoo-community.org/",
    "author": "LasLabs, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
        "mail",
        "web",
    ],
    "data": [
        "data/export.xml",
        "security/export_security.xml",
        "security/ir.model.access.csv",
        "views/export_view.xml",
    ],
}
