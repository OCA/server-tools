# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Field Float Nullable",
    "summary": """
        New float field that supports NULL values instead of defaulting to 0.0""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "depends": ["base", "web"],
    "maintainers": ["samirGuesmi"],
    "assets": {
        "web.assets_backend": [
            "field_float_nullable/static/src/xml/float_field.xml",
            "field_float_nullable/static/src/js/float_field.esm.js",
            "field_float_nullable/static/src/js/float_nullable_search.esm.js",
        ],
    },
    "installable": True,
}
