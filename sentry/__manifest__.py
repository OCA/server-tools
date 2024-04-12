# Copyright 2016-2017 Versada <https://versada.eu/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sentry",
    "summary": "Report Odoo errors to Sentry",
    "version": "16.0.3.0.2",
    "category": "Extra Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "Mohammed Barsi,"
    "Versada,"
    "Nicolas JEUDY,"
    "Odoo Community Association (OCA),"
    "Vauxoo",
    "maintainers": ["barsi", "naglis", "versada", "moylop260", "fernandahf"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [
            "sentry_sdk<=1.9.0",
        ]
    },
    "depends": [
        "base",
    ],
    "post_load": "post_load",
}
