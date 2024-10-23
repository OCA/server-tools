# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Auto Export",
    "summary": """
        Configurable asynchronous exports with rows and columns filtering from
        a selected data model.""",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "license": "AGPL-3",
    "author": "Odoo Community Association (OCA), ACSONE SA/NV",
    "website": "https://github.com/OCA/server-tools",
    "depends": [
        # ODOO
        "base",
        # OCA
        "connector",
        "queue_job",
    ],
    "data": [
        "security/groups.xml",
        "security/auto_export.xml",
        "security/auto_export_backend.xml",
        "security/auto_export_rules.xml",
        "data/queue_job_channel.xml",
        "data/queue_job_function.xml",
        "data/auto_export_backend.xml",
        "views/auto_export.xml",
        "views/menus.xml",
    ],
    "application": True,
}
