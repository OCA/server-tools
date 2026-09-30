{
    "name": "Issue Auto Send",
    "summary": "Send Odoo server error tracebacks to a GitHub repository or by email",
    "version": "19.0.1.0.11",
    "category": "Tools",
    "author": "it-fact, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "license": "LGPL-3",
    "depends": ["web"],
    "data": [
        "security/ir.model.access.csv",
        "security/issue_auto_send_security.xml",
        "views/issue_auto_send_log_views.xml",
        "views/res_company_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "issue_auto_send/static/src/web/error_dialog/error_dialog_patch.esm.js",
            "issue_auto_send/static/src/web/error_dialog/error_dialog_patch.scss",
            "issue_auto_send/static/src/web/error_dialog/error_dialog_patch.xml",
        ],
    },
    "installable": True,
    "application": False,
}
