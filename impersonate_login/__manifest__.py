# Copyright 2024 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Impersonate Login",
    "summary": "tools",
    "version": "14.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["Kev-Roche"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "web",
        "mail",
    ],
    "data": [
        "views/assets.xml",
        "views/res_users.xml",
        "views/impersonate_log.xml",
        "security/group.xml",
        "security/ir.model.access.csv",
    ],
    "qweb": [
        "static/src/xml/user_menu.xml",
    ],
}
