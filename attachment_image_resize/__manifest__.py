# Copyright 2024 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Attachment Image Resize",
    "summary": "Resize attachment images with custom resolution per model",
    "version": "15.0.1.0.0",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "category": "Tools",
    "license": "AGPL-3",
    "depends": ["base_setup"],
    "data": [
        "data/scheduler.xml",
        "views/ir_model_views.xml",
    ],
    "maintainers": ["yostashiro", "aungkokolin1997"],
    "installable": True,
}
