# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Security Group Recorder",
    "version": "13.0.0.0.0",
    "development_status": "Alpha",
    "summary": "Enables the creation of user groups more quickly and efficiently.",
    "author": "ForgeFlow," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "license": "LGPL-3",
    "depends": ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/security_group_recorder_templates.xml",
        "wizard/template_security_group.xml",
    ],
    "installable": True,
    "application": False,
    "qweb": [
        "static/src/xml/play_button.xml",
    ],
    "auto_install": False,
}
