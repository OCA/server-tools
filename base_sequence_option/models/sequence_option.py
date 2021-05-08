# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import safe_eval


class BaseSequenceOption(models.Model):
    _name = "base.sequence.option"
    _description = "Sequence Option Base Model"

    name = fields.Char(readonly=True)
    use_sequence_option = fields.Boolean(
        string="Use sequence options",
        help="If checked, Odoo will try to find the new matching sequence first, "
        "if not found, fall back to use the original Odoo sequence.",
    )
    model = fields.Selection(
        selection=[],
        string="Apply On Model",
        required=True,
        readonly=True,
    )
    option_ids = fields.One2many(
        string="Sequence Options",
        comodel_name="sequence.option",
        inverse_name="base_id",
    )


class SequenceOption(models.Model):
    _name = "sequence.option"
    _description = "Sequence Options"

    base_id = fields.Many2one(
        comodel_name="base.sequence.option",
        index=True,
        required=True,
        ondelete="cascade",
    )
    name = fields.Char(
        string="Description",
        required=True,
    )
    model = fields.Selection(
        related="base_id.model",
        store=True,
        readonly=True,
    )
    use_sequence_option = fields.Boolean(
        related="base_id.use_sequence_option",
        store=True,
    )
    filter_domain = fields.Char(
        string="Apply On",
        default="[]",
        help="Find matching option by document values",
    )
    sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Sequence",
        required=True,
    )
    prefix = fields.Char(
        related="sequence_id.prefix",
        string="Prefix",
        readonly=True,
    )
    suffix = fields.Char(
        related="sequence_id.suffix",
        string="Suffix",
        readonly=True,
    )
    implementation = fields.Selection(
        related="sequence_id.implementation",
        string="Implementation",
        readonly=True,
    )

    def get_model_options(self, model):
        return self.sudo().search(
            [("use_sequence_option", "=", True), ("model", "=", model)]
        )

    def get_sequence(self, record, options=False):
        """
        Find sequence option that match the record values
        """
        if not options:
            options = self.get_model_options(record._name)
        sequence = self.env["ir.sequence"]
        for option in options:
            domain = safe_eval.safe_eval(option.filter_domain)
            if record.sudo().filtered_domain(domain):
                if sequence:  # Do not allow > 1 match
                    raise ValidationError(
                        _("Multiple optional sequences found for this model!")
                    )
                sequence = option.sequence_id
        return sequence
