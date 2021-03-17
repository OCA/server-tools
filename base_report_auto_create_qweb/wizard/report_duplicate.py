# Authors: See README.RST for Contributors
# Copyright 2015-2017
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class IrActionsReportDuplicate(models.TransientModel):
    _name = "ir.actions.report.duplicate"
    _description = "Duplicate Qweb report"

    suffix = fields.Char(
        string="Suffix", help="This suffix will be added to the report"
    )

    def duplicate_report(self):
        self.ensure_one()
        active_id = self.env.context.get("active_id")
        model = self.env.context.get("active_model")
        if model:
            record = self.env[model].browse(active_id)
            record.with_context(suffix=self.suffix, enable_duplication=True).copy()
        return {}
