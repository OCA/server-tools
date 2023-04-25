# Copyright 2016-2017 Versada <https://versada.eu/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sentry",
    "summary": "Report Odoo errors to Sentry. Based on Odoo 16 version backported to Odoo 11 by Otrium.",
    "version": "11.0.0.0.1",
    "category": "Extra Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "Mohammed Barsi,"
    "Versada,"
    "Nicolas JEUDY,"
    "Odoo Community Association (OCA),"
    "Vauxoo",
    "Otrium"
    "maintainers": ["barsi", "naglis", "versada", "moylop260", "fernandahf"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": ["sentry_sdk"]
    },
    "depends": [
        "base",
    ],
    "post_load": "post_load",
}
