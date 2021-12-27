# Copyright 2015-2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Mail cleanup",
    "version": "14.0.1.0.0",
    "category": "Tools",
    "summary": "Mark as read or delete mails after a set time",
    "author": "Camptocamp, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/server-tools",
    "depends": [
        "mail_environment",
    ],
    "data": [
        "views/mail_view.xml",
    ],
    "installable": True,
    "application": False,
}
