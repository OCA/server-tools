{
    "name": "Odoo Vapi Call Integration",
    "author": "Juan Puig, Polpo.uy",
    "website": "https://polpo.uy",
    "category": "Extra Tools",
    "version": "16.0.1.0.0",
    "depends": ["base", "web"],
    'icon': '/polpo_vapi_integration/static/description/icon.png',
    "data": [
        "security/ir.model.access.csv",
        "views/vapi_integration_vapi_sdk.xml",
        "views/vapi_log_views.xml",
        "views/res_config_settings_views.xml",
        "views/res_users_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/polpo_vapi_integration/static/src/js/vapi_integration_widget.js",
        ],
    },
    "installable": True,
    'license': 'AGPL-3',
    "application": False,
}
