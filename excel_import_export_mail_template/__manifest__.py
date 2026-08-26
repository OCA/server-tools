# Copyright 2024 Akretion (https://www.akretion.com).
# @author Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Excel Import/Export Mail Template",
    "summary": """Extended version of the import/export module to
    add excel files to the email template""",
    "version": "16.0.1.1.0",
    "author": "Akretion,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/server-tools",
    "category": "Tools",
    "depends": ["excel_import_export"],
    "data": [
        "views/xlsx_template_view.xml",
    ],
    "installable": True,
    "maintainers": ["mathieudelva"],
}
