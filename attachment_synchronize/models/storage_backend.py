# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StorageBackend(models.Model):
    _inherit = "storage.backend"

    synchronize_task_ids = fields.One2many(
        "attachment.synchronize.task", "backend_id",
        string="Tasks")
