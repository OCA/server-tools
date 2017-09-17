# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Import from Odoo",
    "version": "8.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Tools",
    "summary": "Import records from another Odoo instance",
    "depends": [
        'base',
    ],
    "demo": [
        "demo/res_users.xml",
        "demo/import_odoo_database.xml",
        "demo/import_odoo_database_field.xml",
        "demo/import_odoo_database_model.xml",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/import_odoo_database.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "external_dependencies": {
        "python": ['erppeek'],
    },
}
