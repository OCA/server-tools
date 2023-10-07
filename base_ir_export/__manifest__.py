# Copyright 2020 ACSONE
# Nans Lefebvre <nans.lefebvre@acsone.eu>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Base Ir Exports",
    "summary": "Module providing a wizard to create exports and views on ir.exports",
    "version": "13.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://github.com/OCA/server-tools",
    "author": "Acsone, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["base"],
    "data": ["wizard/ir_exports_wizard.xml", "views/ir_exports_view.xml"],
    "demo": [],
}
