# Copyright 2019 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "SQL Export Excel",
    "version": "14.0.1.1.0",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "license": "AGPL-3",
    "category": "Generic Modules/Others",
    "summary": "Allow to export a sql query to an excel file.",
    "depends": ["sql_export"],
    "external_dependencies": {
        "python": [
            "openpyxl",
        ],
    },
    "data": [
        "views/sql_export_view.xml",
    ],
    "installable": True,
}
