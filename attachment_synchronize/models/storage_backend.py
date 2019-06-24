# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StorageBackend(models.Model):
    _inherit = "storage.backend"

    task_ids = fields.One2many(
        "storage.backend.task", "backend_id",
        string="Tasks")
