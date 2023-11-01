# Copyright 2021 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Restrict Deletion of Attachments",
    "version": "14.0.1.0.0",
    "depends": [
        "base",
        "base_setup",
    ],
    "website": "https://github.com/OCA/server-tools",
    "author": "Quartile Limited, Akretion, Odoo Community Association (OCA)",
    "category": "Tools",
    "license": "AGPL-3",
    "maintainers": ["yostashiro", "Kev-Roche"],
    "data": [
        "views/ir_model_views.xml",
        "views/res_groups_views.xml",
        "views/res_users_views.xml",
        "views/res_config_view.xml",
    ],
    "installable": True,
}
