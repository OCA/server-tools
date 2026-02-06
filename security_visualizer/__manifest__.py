# Copyright 2026 Kobros-Tech Ltd (http://kobros-tech.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Permissions & Access Rule Visualizer",
    "version": "16.0.1.0.0",
    "category": "Tools",
    "summary": "Visualize and debug Odoo security rules and access permissions",
    "author": "Kobros-Tech, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "license": "AGPL-3",
    "depends": [
        "base",
        "web",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/security_visualizer_views.xml",
        "views/security_visualizer_menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "security_visualizer/static/src/components/access_matrix/*",
            "security_visualizer/static/src/components/rule_explainer/*",
            "security_visualizer/static/src/components/security_visualizer/*",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
