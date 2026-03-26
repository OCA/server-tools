# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Excel Import Required Fields",
    "summary": "Enforce required fields during excel import",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "author": "Heliconia Solutions Pvt. Ltd., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "license": "AGPL-3",
    "development_status": "Beta",
    "maintainers": ["Bhavesh Heliconia"],
    "depends": ["excel_import_export"],
    "data": [
        "views/xlsx_template_view.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
