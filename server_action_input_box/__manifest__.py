# Copyright 2024 jesanmor - Jesús Sánchez <jesanmor.dev@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Server Action Input Box",
    "summary": """Shows a parameter input box in a server action
    under the 'Action' menu of the model.""",
    "author": "Jesús Sánchez - jesanmor, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "maintainers": ["jesanmor"],
    "development_status": "Production/Stable",
    "category": "technical",
    "version": "17.0.1.0.0",
    "depends": [
        "base",
        "web",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/server_action_input_box_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "server_action_input_box/static/src/js/show_server_action_input_box.esm.js",
            "server_action_input_box/static/src/xml/show_server_action_input_box.xml",
        ],
    },
    "license": "AGPL-3",
    "installable": True,
    "images": ["static/description/icon.png"],
    "uninstall_hook": "uninstall_hook",
}
