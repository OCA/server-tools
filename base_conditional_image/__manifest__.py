# Copyright 2019-2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Conditional Images",
    "summary": "This module extends the functionality to support conditional images",
    "version": "14.0.3.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Misc",
    "depends": [
        "mail",
    ],
    "website": "https://github.com/OCA/server-tools",
    "data": [
        "data/ir_cron.xml",
        "views/conditional_image_view.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
