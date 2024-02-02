# -*- coding: utf-8 -*-
# Authors: See README.RST for Contributors
# Copyright 2015-2017
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Report qweb auto generation",
    "version": "10.0.1.0.0",
    "depends": [
        "report",
    ],
    "external_dependencies": {
        "python": [
            "unidecode",
        ],
    },
    "author": "AvanzOSC, "
              "Tecnativa, "
              "Odoo Community Association (OCA), ",
    "website": "https://github.com/OCA/server-tools"
               "/tree/10.0/base_report_auto_create_qweb",
    "license": "AGPL-3",
    "category": "Tools",
    "data": [
        "wizard/report_duplicate_view.xml",
        "views/report_xml_view.xml",
    ],
    'installable': True,
}
