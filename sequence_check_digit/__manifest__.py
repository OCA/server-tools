# -*- coding: utf-8 -*-
# Copyright (C) 2017 Creu Blanca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Check Digit on Sequences",
    "version": "10.0.1.0.0",
    "category": "Reporting",
    "website": "https://odoo-community.org",
    "author": "Creu Blanca, "
              "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "summary": "Adds a check digit on sequences",
    "depends": [
        "base",
    ],
    "data": [
        "views/sequence_views.xml",
    ],
    "external_dependencies": {
        "python": [
            "stdnum"
        ],
    }
}
