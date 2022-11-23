# © 2022 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Import Processor",
    "summary": "Generic import processor",
    "license": "AGPL-3",
    "version": "15.0.1.0.0",
    "website": "https://www.initos.com",
    "application": True,
    "author": "initOS GmbH",
    "category": "Tools",
    "depends": [
        "base",
        "web",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/import_processor_views.xml",
        "wizards/import_processor_wizard_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/import_processor/static/src/*.js",
        ],
        "web.assets_qweb": [
            "/import_processor/static/src/*.xml",
        ],
    },
}
