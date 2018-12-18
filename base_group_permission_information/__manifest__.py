# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "base_group_permission_information",
    "summary": "Compute and display permission information per group",
    "version": "10.0.1.0.0",
    "development_status": "Alpha",
    "category": "Tools",
    "website": "https://github.com/OCA/server-tools>",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["damdam-s"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
    ],
    "data": [
        "views/groups.xml",
        "views/users.xml",
        "data/ir_cron.xml",
    ],
}
