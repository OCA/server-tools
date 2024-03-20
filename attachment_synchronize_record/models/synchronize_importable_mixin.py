# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime

from odoo import fields, models


class SynchronizeImportableMixin(models.AbstractModel):
    _name = "synchronize.importable.mixin"
    _description = "Synchronizable import mixin"

    import_date = fields.Date()
    import_file_id = fields.Many2one("attachment.queue")
    import_error = fields.Text(related="import_file_id.state_message", readonly=True)

    def track_model_import(self, attachment_queue):
        self.write(
            {
                "import_date": datetime.datetime.now(),
                "import_file_id": attachment_queue.id,
            }
        )
