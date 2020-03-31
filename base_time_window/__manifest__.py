# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Base Time Window",
    "summary": "Base model to handle time windows",
    "version": "13.0.1.0.0",
    "category": "Technical Settings",
    "author": "ACSONE SA/NV, Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/server-tools",
    "depends": ["base"],
    "data": [
        "data/time_weekday.xml",
        "security/ir.model.access.xml"
    ],
    "installable": True,
}
