# Copyright 2014-2016 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp SA <https://camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Database cleanup",
    "version": "15.0.1.0.2",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "depends": ["base"],
    "license": "AGPL-3",
    "category": "Tools",
    "data": [
        "views/purge_wizard.xml",
        "views/purge_menus.xml",
        "views/purge_modules.xml",
        "views/purge_models.xml",
        "views/purge_columns.xml",
        "views/purge_tables.xml",
        "views/purge_data.xml",
        "views/create_indexes.xml",
        "views/purge_properties.xml",
        "views/menu.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
