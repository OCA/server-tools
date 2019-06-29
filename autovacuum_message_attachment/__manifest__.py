# Copyright (C) 2018 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "AutoVacuum Mail Message",
    "version": "12.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "summary": "Automatically delete old mail messages to clean database",
    "depends": [
        "mail",
    ],
    "data": [
        "data/data.xml",
        "views/message_rule_vacuum.xml",
        "security/ir.model.access.csv",
    ],
}
