# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Base video link",
    "summary": "Add the possibility to link video on record",
    "version": "14.0.1.1.2",
    "development_status": "Beta",
    "category": "Others",
    "website": "https://github.com/OCA/server-tools",
    "author": " Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
    ],
    "data": [
        "views/video_provider_view.xml",
        "views/video_video_view.xml",
        "views/menu_view.xml",
        "data/video_provider_data.xml",
        "security/ir.model.access.csv",
    ],
    "demo": ["demo/video_demo.xml"],
}
