# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Remote Export RPC",
    "summary": "Crear/actualizar registros en un Odoo remoto vía RPC",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "category": "Tools",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/remote_odoo_instance_views.xml",
        "views/remote_odoo_match_config_views.xml",
        "wizard/remote_odoo_export_wizard_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "maintainers": ["carlosdauden"],
}
