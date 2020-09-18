# @ 2016 Florian DA COSTA @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
from odoo import api, models, fields


class AttachmentQueue(models.Model):
    _inherit = "attachment.queue"

    task_id = fields.Many2one("attachment.synchronize.task", string="Task")
    method_type = fields.Selection(related="task_id.method_type")
    storage_backend_id = fields.Many2one(
        "storage.backend",
        string="Storage Backend",
        related="task_id.backend_id",
        store=True,
    )

    def _run(self):
        super()._run()
        if self.task_id and self.task_id.method_type == "export":
            path = os.path.join(self.task_id.filepath, self.datas_fname)
            self.storage_backend_id._add_b64_data(path, self.datas)

    def _get_failure_emails(self):
        res = super()._get_failure_emails()
        if self.task_id.failure_emails:
            res = self.task_id.failure_emails
        return res
