# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class IrSequence(models.Model):
    _inherit = "ir.sequence"

    def next_by_id(self, sequence_date=None):
        sequence_id = self.env.context.get("sequence_option_id", False)
        if sequence_id:
            self = self.browse(sequence_id)
        return super().next_by_id(sequence_date=sequence_date)

    @api.model
    def next_by_code(self, sequence_code, sequence_date=None):
        sequence_id = self.env.context.get("sequence_option_id", False)
        if sequence_id:
            self = self.browse(sequence_id)
            return super().next_by_id(sequence_date=sequence_date)
        return super().next_by_code(sequence_code, sequence_date=sequence_date)
