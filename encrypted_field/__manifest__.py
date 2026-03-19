# -*- coding: utf-8 -*-
{
    "name": "Encrypted Field",
    "version": "17.0.1.0.0",
    "category": "Technical",
    "summary": "Encrypted field types for sensitive data storage",
    "description": """
        Provides encrypted field types for storing sensitive data like SSN,
        credit card numbers, medical IDs, etc.

        Features:
        - Encrypted field wrapper for any field type
        - AES encryption via Fernet
        - Field-level masking (show last 4 digits, etc.)
        - Group-based access control
        - Audit logging of decryption access
        - Key rotation wizard
        - Migration tool for encrypting existing data

        WARNING: If you lose your encryption key, encrypted data is
        PERMANENTLY UNRECOVERABLE. Back up your key separately from your database.
    """,
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
            "encrypted_field/static/src/js/encrypted_field.js",
            "encrypted_field/static/src/xml/encrypted_field.xml",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
