# Copyright 2020-2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Import Module Group",
    "summary": "Restrict module importation to specific group",
    "version": "13.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://github.com/OCA/server-tools",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": ["base_import_module",],  # noqa: E231
    "data": ["security/res_groups.xml", "views/import_module_group.xml",],  # noqa: E231
}
