# -*- coding: utf-8 -*-
# © 2015 Antiun Ingeniería, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Verify email at signup",
    "summary": "Force uninvited users to use a good email for signup",
    "version": "10.0.1.0.0",
    "category": "Authentication",
    "website": "http://www.tecnativa.com",
    "author": "Antiun Ingeniería S.L., "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    'installable': True,
    "external_dependencies": {
        "python": [
            "lxml",
            "validate_email",
        ],
    },
    "depends": [
        "auth_signup",
    ],
    "data": [
        "views/signup.xml",
    ],
}
