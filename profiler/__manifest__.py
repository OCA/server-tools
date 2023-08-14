{
    "name": "profiler",
    "author": "Vauxoo, Sunflower IT, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "category": "Tests",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["web_tour"],
    "data": [
        "security/ir.model.access.csv",
        "views/profiler_profile_view.xml",
        "views/assets.xml",
    ],
    "post_load": "post_load",
    "installable": True,
}
