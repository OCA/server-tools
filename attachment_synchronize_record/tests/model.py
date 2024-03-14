# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import csv
from io import StringIO

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = [
        "res.partner",
        "synchronize.exportable.mixin",
        "synchronize.importable.mixin",
    ]
    _name = "res.partner"

    def _prepare_export_data(self, _):
        res = []
        for rec in self:
            res += [{"name": rec.name}]
        return res

    def _get_export_task(self):
        return self.env.ref("attachment_synchronize.export_to_filestore")

    def _get_export_name(self):
        return self[0].name

    @property
    def record_per_file(self):
        return 10


class AttachmentQueue(models.Model):
    _inherit = "attachment.queue"

    file_type = fields.Selection(
        selection_add=[("test_import", "Test import file type")]
    )

    def _run(self):
        if self.file_type == "test_import":
            return self._run_test_import()
        return super()._run()

    def _run_test_import(self):
        reader = csv.reader(
            StringIO(base64.b64decode(self.datas).decode("utf-8")),
            delimiter=";",
        )
        for row in reader:
            partner = self.env["res.partner"].search([("name", "=", row[0])])
            partner.write({"name": row[1]})
            partner.track_model_import(self)
