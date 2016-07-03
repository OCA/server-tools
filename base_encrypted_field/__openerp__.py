# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Encrypted fields",
    "version": "8.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Security",
    "summary": "Allow users to encrypt fields",
    "depends": [
        'web',
    ],
    "data": [
        "wizards/base_encrypted_field_select_or_create_group.xml",
        "wizards/base_encrypted_field_get_passphrase.xml",
        "wizards/base_encrypted_field_update_key.xml",
        "views/res_users.xml",
        'views/templates.xml',
        'security/ir.model.access.csv',
    ],
    "qweb": [
        'static/src/xml/base_encrypted_field.xml',
    ],
    "test": [
    ],
    "images": [
    ],
    "pre_init_hook": False,
    "post_init_hook": False,
    "uninstall_hook": False,
    "auto_install": False,
    "installable": True,
    "application": False,
    "external_dependencies": {
        'python': [],
    },
}
