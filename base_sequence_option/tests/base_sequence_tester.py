# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class BaseSequenceTester(models.Model):
    _name = "base.sequence.tester"
    _description = "Base Sequence Tester"

    name = fields.Char(default="/")
    test_type = fields.Selection(selection=[("a", "A"), ("b", "B")])

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            seq = self.env["ir.sequence.option.line"].get_sequence(self.new(vals))
            if (
                seq
            ):  # use sequence from sequence.option, instead of base.sequence.tester
                self = self.with_context(sequence_option_id=seq.id)
            new_seq = self.env["ir.sequence"].next_by_code("base.sequence.tester")
            vals["name"] = new_seq
        return super().create(vals_list)


class IrSequenceOption(models.Model):
    _inherit = "ir.sequence.option"

    model = fields.Selection(
        selection_add=[("base.sequence.tester", "base.sequence.tester")],
        ondelete={"base.sequence.tester": "cascade"},
    )
