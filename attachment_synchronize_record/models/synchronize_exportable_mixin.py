# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import csv
import datetime
from io import StringIO

from odoo import api, fields, models
from odoo.tools import config


class SynchronizeExportableMixin(models.AbstractModel):
    _name = "synchronize.exportable.mixin"
    _description = "Synchronizable export mixin"

    export_date = fields.Datetime(readonly=True)
    export_attachment_id = fields.Many2one(
        "attachment.queue", index=True, readonly=True
    )
    export_error = fields.Char(readonly=True, index=True)

    @property
    def record_per_file(self):
        return 1

    def button_trigger_export(self):
        self.synchronize_export(raise_error=True)

    def _get_export_data(self, raise_error=False):
        data = []
        records = self.browse()
        sequence = 0
        for rec in self:
            try:
                with self._cr.savepoint():
                    data += rec._prepare_export_data(sequence)
                    records |= rec
                    rec.export_error = None
                    sequence += 1
            except Exception as e:
                if raise_error:
                    raise
                if "pdb" in config.get("dev_mode"):
                    raise
                rec.export_error = str(e)
                continue
            if len(records) >= self.record_per_file:
                yield records, data
                data = []
                records = self.browse()
                sequence = 0
        if len(records):
            yield records, data

    def synchronize_export(self, raise_error=False):
        attachments = self.env["attachment.queue"]
        for records, data in self._get_export_data(raise_error=raise_error):
            vals = records._prepare_aq_vals(data)
            attachment = self.env["attachment.queue"].create(vals)
            records.track_export(attachment)
            attachments |= attachment
        return attachments

    def track_export(self, attachment):
        self.export_date = datetime.datetime.now()
        self.export_attachment_id = attachment
        if len(self.ids) == 1:
            attachment.res_model = self._name
            attachment.res_id = self.id

    def _prepare_export_data(self, idx) -> list:
        raise NotImplementedError

    def _get_export_task(self):
        raise NotImplementedError

    def _prepare_aq_vals(self, data):
        task = self._get_export_task()
        return {
            "name": self._get_export_name(),
            "datas": base64.b64encode(self._prepare_aq_data(data)),
            "task_id": task.id,
            "file_type": task.file_type,
        }

    def _prepare_aq_data(self, data):
        return self._prepare_aq_data_csv(data)

    def _prepare_aq_data_csv(self, data):
        csv_file = StringIO()
        delimiter = self.env.context.get("csv_delimiter") or ";"
        writer = csv.DictWriter(
            csv_file, fieldnames=data[0].keys(), delimiter=delimiter
        )
        for row in data:
            writer.writerow(row)
        csv_file.seek(0)
        return csv_file.getvalue().encode("utf-8")

    def _get_export_name(self):
        raise NotImplementedError

    @api.model
    def _schedule_export(self, *args, domain=False):
        if not domain:
            domain = []
        recs = self.search(domain)
        if not recs:
            return self.env["attachment.queue"]
        return recs.with_context(
            **recs._synchronize_context_hook(args)
        ).synchronize_export()

    def _synchronize_context_hook(self, *args):
        return {}
