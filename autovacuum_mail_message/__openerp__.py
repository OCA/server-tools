# -*- coding: utf-8 -*-
# Copyright (C) 2018 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "AutoVacuum Mail Message",
    "version": "9.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "summary": "Automatic Delete old mail message to clean database",
    "depends": [
        "mail",
    ],
    "data": [
        "data/data.xml",
        "views/message_rule_vacuum.xml",
        "security/ir.model.access.csv",
    ],
}
