{
    "name": "Attachment Logging",
    "version": "16.0.1.0.0",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "summary": "Show attachment information in chatter",
    "website": "https://github.com/OCA/server-tools",
    "license": "AGPL-3",
    "category": "Hidden/Tools",
    "depends": ["mail"],
    "data": [
        "data/mail_message_subtype_data.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "attachment_logging/static/src/models/*",
            "attachment_logging/static/src/components/*/*",
        ]
    },
}
