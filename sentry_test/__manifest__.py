# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "Sentry Test",
    "summary": "Test module for testing sentry integration",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Test",
    "website": "https://github.com/OCA/server-tools",
    "author": " Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "sentry",
        "queue_job",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/wizard_test_sentry_view.xml",
        "data/ir_cron.xml",
    ],
    "demo": [],
}
