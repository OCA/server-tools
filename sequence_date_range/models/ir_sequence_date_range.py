# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class IrSequenceDateRange(models.Model):
    _inherit = 'ir.sequence.date_range'

    @api.multi
    def _next(self):
        """
        Inherit to use the date_to (instead of date_from) as the base date
        :return: str
        """
        seq_date_range = self.env.context.get('ir_sequence_date_range')
        if seq_date_range and self.sequence_id.date_range_field:
            expected_value = self[self.sequence_id.date_range_field]
            if seq_date_range != expected_value:
                self = self.with_context(ir_sequence_date_range=expected_value)
        return super(IrSequenceDateRange, self)._next()
