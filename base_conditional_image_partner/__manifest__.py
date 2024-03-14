# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Conditional Images for Partners",
    "summary": "This module add the functionality to support conditional images to partners",
    "version": "15.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Misc",
    "depends": [
        "contacts",
        "base_conditional_image",
    ],
    "data": [
        "views/image_view.xml",
    ],
    "website": "https://github.com/OCA/server-tools",
    "installable": True,
}
