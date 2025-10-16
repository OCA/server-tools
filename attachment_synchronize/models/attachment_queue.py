# @ 2016 Florian DA COSTA @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64

from odoo import api, fields, models

from odoo.addons.queue_job.exception import RetryableJobError


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

    def _write_file_to_remote(self, fs, full_path):
        self.ensure_one()
        data = base64.b64decode(self.datas)
        with fs.open(full_path, "wb") as f:
            f.write(data)

    def _run(self):
        res = super()._run()
        if self.file_type == "export":
            try:
                fs = self.fs_storage_id.fs
                folder_path = self.task_id.filepath
                full_path = (
                    folder_path and fs.sep.join([folder_path, self.name]) or self.name
                )
                # create missing folders if necessary :
                if folder_path and not fs.exists(folder_path):
                    fs.makedirs(folder_path)
                self._write_file_to_remote(fs, full_path)
            except TimeoutError as err:
                raise RetryableJobError(
                    str(err),
                    seconds=self._timeout_retry_seconds(),
                ) from err
        return res

    def _timeout_retry_seconds(self):
        return 60 * 60 * 4

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
