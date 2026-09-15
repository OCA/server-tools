# Copyright 2012 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Attachment Queue Email",
    "version": "18.0.1.0.0",
    "author": "Akretion,Odoo Community Association (OCA)",
    "category": "Generic Modules",
    "summary": "Create attachment from emails to be processed depending on their type",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/server-tools",
    "maintainers": ["florian-dacosta", "sebastienbeau", "bealdav"],
    "depends": ["attachment_queue", "mail"],
    "demo": [],
    "data": [
        "security/ir.model.access.csv",
        "views/fetchmail_attachment_condition.xml",
        "views/fetchmail_server.xml",
    ],
    "installable": True,
    "images": [],
}
