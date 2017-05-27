# -*- coding: utf-8 -*-
# Authors: See README.RST for Contributors
# Copyright 2015-2016 See __openerp__.py for Authors
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Report qweb auto generation",
    "version": "9.0.1.0.0",
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
    "website": "https://github.com/OCA/server-tools",
    "license": "AGPL-3",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
    ],
    "category": "Tools",
    "data": [
        "wizard/report_duplicate_view.xml",
        "views/report_xml_view.xml",
    ],
    'installable': True,
}
