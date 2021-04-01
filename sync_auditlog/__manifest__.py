# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sync Audit Log",
    "version": "14.0.1.0.0",
    "author": "Open Source Integrators, ABF OSIELL,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/server-tools",
    "category": "Tools",
    "depends": ["auditlog", "mail"],
    "data": [
        "data/cron_prepare_events.xml",
        "data/cron_push_pull_event_data.xml",
        "data/cron_initialize_master_data.xml",
        "data/cron_apply_event_data.xml",
        "views/remote_server_view.xml",
        "views/auditlog_view.xml",
        "security/ir.model.access.csv",
    ],
    "application": True,
    "installable": True,
}
