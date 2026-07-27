# Copyright 2026 Pol Reig <pol.reig@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Global Undo & Redo",
    "summary": "Undo and redo backend operations with Ctrl+Z, with history and trash",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "author": "Pol Reig, QubiQ, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "license": "AGPL-3",
    "development_status": "Beta",
    "maintainers": ["polreig"],
    "application": False,
    "installable": True,
    "depends": ["base", "web"],
    "data": [
        "security/global_undo_security.xml",
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "data/ir_config_parameter_data.xml",
        "views/global_undo_transaction_views.xml",
        "views/global_undo_operation_views.xml",
        "views/global_undo_action_views.xml",
        "views/global_undo_exclusion_views.xml",
        "views/global_undo_menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "global_undo/static/src/global_undo_systray/global_undo_systray.scss",
            "global_undo/static/src/global_undo_service/global_undo_service.esm.js",
            "global_undo/static/src/global_undo_systray/global_undo_systray.esm.js",
            "global_undo/static/src/global_undo_systray/global_undo_systray.xml",
        ],
        "web.assets_tests": [
            "global_undo/static/tests/tours/global_undo_tour.esm.js",
        ],
    },
}
