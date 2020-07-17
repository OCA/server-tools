# Copyright 2015 Florian DA COSTA @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Attachment Queue",
    "version": "12.0.3.0.0",
    "author": "Akretion,Odoo Community Association (OCA)",
    "summary": "Base module adding the concept of queue for processing files",
    "website": "https://github.com/OCA/server-tools",
    "maintainers": ["florian-dacosta", "sebastienbeau"],
    "license": "AGPL-3",
    "category": "Generic Modules",
    "depends": ["base", "mail"],
    "data": [
        "views/attachment_queue_view.xml",
        "security/ir.model.access.csv",
        "data/cron.xml",
        "data/ir_config_parameter.xml",
        "data/mail_template.xml",
    ],
    "demo": ["demo/attachment_queue_demo.xml"],
    "installable": True,
}
