# Copyright 2017 Simone Orsi
# Copyright 2018 Creu Blanca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Base Fontawesome",
    "summary": """Up to date Fontawesome resources.""",
    "version": "18.0.2.0.0",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/server-tools",
    "author": "Camptocamp,Creu Blanca,Odoo Community Association (OCA)",
    "depends": ["web"],
    "assets": {
        "web.assets_backend": [
            (
                "replace",
                "web/static/src/libs/fontawesome/css/font-awesome.css",
                "base_fontawesome/static/src/css/fontawesome.css",
            ),
            "base_fontawesome/static/lib/fontawesome-6.7.2/css/all.css",
            "base_fontawesome/static/lib/fontawesome-6.7.2/css/v4-shims.css",
        ],
        "web.assets_frontend": [
            (
                "replace",
                "web/static/src/libs/fontawesome/css/font-awesome.css",
                "base_fontawesome/static/src/css/fontawesome.css",
            ),
            "base_fontawesome/static/lib/fontawesome-6.7.2/css/all.css",
            "base_fontawesome/static/lib/fontawesome-6.7.2/css/v4-shims.css",
        ],
        "web.report_assets_common": [
            (
                "replace",
                "web/static/src/libs/fontawesome/css/font-awesome.css",
                "base_fontawesome/static/src/css/fontawesome.css",
            ),
            "base_fontawesome/static/lib/fontawesome-6.7.2/css/all.css",
            "base_fontawesome/static/lib/fontawesome-6.7.2/css/v4-shims.css",
        ],
    },
}
