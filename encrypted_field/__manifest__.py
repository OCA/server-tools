{
    "name": "Encrypted Field",
    "version": "17.0.1.0.0",
    "category": "Technical",
    "summary": "Encrypted field types for sensitive data storage",
    "author": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "maintainers": ["jimkring"],
    "license": "LGPL-3",
    "depends": ["base"],
    "external_dependencies": {
        "python": ["cryptography"],
    },
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "wizards/key_rotation_wizard_views.xml",
        "wizards/migration_wizard_views.xml",
        "views/audit_log_views.xml",
        "views/menu.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "encrypted_field/static/src/js/encrypted_field.esm.js",
            "encrypted_field/static/src/xml/encrypted_field.xml",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
