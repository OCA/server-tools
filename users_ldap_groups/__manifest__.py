# Copyright 2020 initOS GmbH
# Copyright 2012-2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "LDAP groups assignment",
    "version": "11.0.1.0.0",
    "depends": ["auth_ldap"],
    "author": "initOS GmbH, Therp BV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "license": "AGPL-3",
    "summary": "Adds user accounts to groups based on rules defined "
    "by the administrator.",
    "category": "Authentication",
    "data": [
        'views/base_config_settings.xml',
        'security/ir.model.access.csv',
    ],
    "external_dependencies": {
        'python': ['ldap'],
    },
}
