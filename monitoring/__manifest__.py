# © 2023 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Monitoring",
    "version": "15.0.1.0.0",
    "category": "Extra Tools",
    "author": "initOS GmbH, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "license": "AGPL-3",
    "summary": "Generic monitoring of Odoo instances",
    "depends": ["mail", "web"],
    "data": [
        "data/ir_cron.xml",
        "security/ir.model.access.csv",
        "views/menuitems.xml",
        "views/monitoring_views.xml",
        "views/monitoring_script_views.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "installable": True,
}
