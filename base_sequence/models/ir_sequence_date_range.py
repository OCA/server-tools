# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from odoo.addons.base.models.ir_sequence import _predict_nextval


class IrSequenceDateRange(models.Model):
    _inherit = "ir.sequence.date_range"

    preview = fields.Char(compute="_compute_preview")

    @api.depends("date_to", "date_from", "number_next_actual")
    def _compute_preview(self):
        for record in self:
            record.preview = record.with_context(
                ir_sequence_date_range=record.date_from,
                ir_sequence_date_range_end=record.date_to,
            ).sequence_id.get_next_char(record.number_next_actual)

    def _next(self):
        return super(
            IrSequenceDateRange,
            self.with_context(ir_sequence_date_range_end=self.date_to),
        )._next()

    def _get_number_next_actual(self):
        """This override method adds support for onchange's pseudo-record."""
        if all(isinstance(seq.id, int) for seq in self):
            return super()._get_number_next_actual()

        for seq in self:
            if seq.sequence_id.implementation != "standard":
                seq.number_next_actual = seq.number_next
            else:
                seq_id = "%03d_%03d" % (seq.sequence_id._origin.id, seq._origin.id)
                seq.number_next_actual = _predict_nextval(self, seq_id)
