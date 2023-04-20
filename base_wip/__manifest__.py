# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Base Wip",
    "summary": """
        Base Work In Progress""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "KMEE,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "depends": [
        "base",
        "board",
    ],
    "data": [
        "security/base_wip.xml",
        "views/base_abstract_wip.xml",
        "views/base_wip.xml",
    ],
    "demo": [],
}
