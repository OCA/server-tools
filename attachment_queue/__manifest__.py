# Copyright 2015 Florian DA COSTA @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Attachment Queue",
    "version": "16.0.1.2.1",
    "author": "Akretion,Odoo Community Association (OCA)",
    "summary": "Base module adding the concept of queue for processing files",
    "website": "https://github.com/OCA/server-tools",
    "maintainers": ["florian-dacosta", "sebastienbeau"],
    "license": "AGPL-3",
    "category": "Generic Modules",
    "depends": ["base", "mail", "queue_job"],
    "data": [
        "views/attachment_queue_view.xml",
        "security/ir.model.access.csv",
        "data/mail_template.xml",
        "data/queue_job_channel.xml",
        "wizards/attachement_queue_reschedule.xml",
    ],
    "demo": ["demo/attachment_queue.xml"],
    "installable": True,
}
