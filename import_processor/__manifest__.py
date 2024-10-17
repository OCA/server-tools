# © 2022 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Import Processor",
    "summary": "Generic import processor",
    "license": "AGPL-3",
    "version": "14.0.1.0.0",
    "website": "https://github.com/OCA/server-tools",
    "application": True,
    "author": "initOS GmbH, Odoo Community Association (OCA)",
    "category": "Tools",
    "depends": [
        "base",
        "web",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/assets.xml",
        "views/import_processor_views.xml",
        "wizards/import_processor_wizard_views.xml",
    ],
    "qweb": [
        "static/src/xml/import_processor.xml",
    ],
    "demo": [
        "data/processor_data.xml",
    ],
}
