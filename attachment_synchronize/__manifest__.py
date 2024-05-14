# @ 2016 florian DA COSTA @ Akretion
# © 2016 @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# @ 2020 Giovanni Serra @ GSlab.it
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Attachment Synchronize",
    "version": "16.0.1.0.1",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "maintainers": ["florian-dacosta", "sebastienbeau", "GSLabIt", "bealdav"],
    "license": "AGPL-3",
    "category": "Generic Modules",
    "depends": [
        "attachment_queue",
        "fs_storage",  # https://github.com/OCA/storage
    ],
    "data": [
        "views/attachment_queue_views.xml",
        "views/attachment_synchronize_task_views.xml",
        "views/storage_backend_views.xml",
        "data/cron.xml",
        "security/ir.model.access.csv",
    ],
    "demo": ["demo/attachment_synchronize_task_demo.xml"],
    "installable": True,
    "development_status": "Beta",
}
