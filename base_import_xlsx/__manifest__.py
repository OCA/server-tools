# Copyright 2022 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Base import Excel",
    "version": "13.0.1.0.0",
    "category": "Generic Modules",
    "summary": "Replace support for excel import by one based on openpyxl",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "depends": ["base_import"],
    "data": ["security/ir.model.access.csv"],
    "license": "AGPL-3",
    "installable": True,
    "external_dependencies": {"python": ["openpyxl"]},
}
