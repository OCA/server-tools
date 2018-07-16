# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Letsencrypt Transip NL",
    "version": "10.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Administration",
    "summary": "Adds support for transip.nl",
    "depends": [
        "letsencrypt",
    ],
    "data": [
        "data/ir_config_parameter.xml",
    ],
    "application": False,
    "external_dependencies": {
        'python': ["transip"],
    },
}
