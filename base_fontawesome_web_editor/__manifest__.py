# Copyright 2025 Heligràfics Fotogrametría S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Base Fontawesome Web Editor",
    "summary": """Integration between base_fontawesome and web_editor """
    """for FontAwesome >= 6.7.2 support.""",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/server-tools",
    "author": "Heligràfics Fotogrametría S.L., Odoo Community Association (OCA)",
    "depends": ["web_editor", "base_fontawesome"],
    "auto_install": True,
    "assets": {
        "web.assets_frontend": [
            "base_fontawesome_web_editor/static/src/js/wysiwyg/fonts.esm.js",
        ],
        "web.assets_backend": [
            "base_fontawesome_web_editor/static/src/js/wysiwyg/fonts.esm.js",
        ],
        "html_editor.assets_media_dialog": [
            "base_fontawesome_web_editor/static/src/js/utils/fonts.esm.js",
        ],
    },
}
