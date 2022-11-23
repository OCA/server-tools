# © 2022 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Import Processor - Asynchronously",
    "summary": "Generic async import processor",
    "license": "AGPL-3",
    "version": "15.0.1.0.0",
    "website": "https://github.com/OCA/server-tools",
    "application": True,
    "author": "initOS GmbH, Odoo Community Association (OCA)",
    "category": "Tools",
    "depends": [
        "import_processor",
        "queue_job",
    ],
    "data": [
        "views/import_processor_views.xml",
    ],
}
