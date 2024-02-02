# -*- coding: utf-8 -*-
# Copyright 2017-2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Import from Odoo",
    "version": "10.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Tools",
    "summary": "Import records from another Odoo instance",
    "website": "https://github.com/OCA/server-tools"
               "/tree/10.0/base_import_odoo",
    "depends": [
        'mail',
    ],
    "demo": [
        "demo/res_partner.xml",
        "demo/res_users.xml",
        "demo/ir_attachment.xml",
        "demo/import_odoo_database.xml",
        "demo/import_odoo_database_field.xml",
        "demo/import_odoo_database_model.xml",
    ],
    "data": [
        "views/import_odoo_database_field.xml",
        "security/ir.model.access.csv",
        "views/import_odoo_database.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "external_dependencies": {
        "python": ['odoorpc'],
    },
}
