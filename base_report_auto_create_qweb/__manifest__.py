# Authors: See README.RST for Contributors
# Copyright 2015-2017
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Report qweb auto generation",
    "version": "16.0.1.0.0",
    "depends": [
        "base",
    ],
    "external_dependencies": {
        "python": [
            "unidecode",
        ],
    },
    "author": "AvanzOSC, Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "license": "AGPL-3",
    "category": "Tools",
    "data": [
        "security/ir.model.access.csv",
        "wizard/report_duplicate_view.xml",
        "views/report_xml_view.xml",
    ],
    "installable": True,
}
