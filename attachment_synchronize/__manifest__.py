# @ 2016 florian DA COSTA @ Akretion
# © 2016 @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# @ 2020 Giovanni Serra @ GSlab.it
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Attachment Synchronize",
    "version": "12.0.1.0.0",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/oca/server-tools",
    "license": "AGPL-3",
    "category": "Generic Modules",
    "depends": ["attachment_queue", "storage_backend"],
    "data": [
        "views/attachment_view.xml",
        "views/task_view.xml",
        "views/storage_backend_view.xml",
        "data/cron.xml",
        "security/ir.model.access.csv",
    ],
    "demo": ["demo/attachment_synchronize_task_demo.xml"],
    "installable": True,
    "application": False,
}
