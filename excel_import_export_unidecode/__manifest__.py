# Copyright 2023 FactorLibre., Ltd (https://factorlibre.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Excel Import/Export/Report: Unidecode",
    "summary": "Add unidecode option to excel import/export/report",
    "version": "17.0.1.0.0",
    "author": "FactorLibre,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/server-tools",
    "category": "Tools",
    "depends": ["excel_import_export"],
    "external_dependencies": {"python": ["unidecode"]},
    "data": ["views/xlsx_template_view.xml"],
    "installable": True,
    "development_status": "Beta",
}
