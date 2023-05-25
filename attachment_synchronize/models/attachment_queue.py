# @ 2016 Florian DA COSTA @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64

from odoo import api, fields, models


class AttachmentQueue(models.Model):
    _inherit = "attachment.queue"

    task_id = fields.Many2one("attachment.synchronize.task", string="Task")
    method_type = fields.Selection(related="task_id.method_type")
    fs_storage_id = fields.Many2one(
        "fs.storage",
        string="Filestore Storage",
        related="task_id.backend_id",
        store=True,
    )
    file_type = fields.Selection(
        selection_add=[("export", "Export File (External location)")]
    )

    def _run(self):
        res = super()._run()
        if self.file_type == "export":
            fs = self.fs_storage_id.fs
            folder_path = self.task_id.filepath
            full_path = (
                folder_path and fs.sep.join([folder_path, self.name]) or self.name
            )
            # create missing folders if necessary :
            if folder_path and not fs.exists(folder_path):
                fs.makedirs(folder_path)
            data = base64.b64decode(self.datas)
            with fs.open(full_path, "wb") as f:
                f.write(data)
        return res

    def _get_failure_emails(self):
        res = super()._get_failure_emails()
        if self.task_id.failure_emails:
            res = self.task_id.failure_emails
        return res

    @api.onchange("task_id")
    def onchange_task_id(self):
        for attachment in self:
            if attachment.task_id.method_type == "export":
                attachment.file_type = "export"
