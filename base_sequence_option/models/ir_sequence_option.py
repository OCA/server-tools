# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import safe_eval


class IrSequenceOption(models.Model):
    _name = "ir.sequence.option"
    _description = "Sequence Option Base Model"
    _check_company_auto = True

    name = fields.Char()
    use_sequence_option = fields.Boolean(
        string="Use sequence options",
        help="If checked, Odoo will try to find the new matching sequence first, "
        "if not found, fall back to use the original Odoo sequence.",
    )
    model = fields.Selection(
        selection=[],
        string="Apply On Model",
        required=True,
        readonly=False,
        index=True,
    )
    option_ids = fields.One2many(
        string="Sequence Options",
        comodel_name="ir.sequence.option.line",
        inverse_name="base_id",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        readonly=False,
        index=True,
        default=lambda self: self.env.company,
        help="Company related to this sequence option",
    )


class IrSequenceOptionLine(models.Model):
    _name = "ir.sequence.option.line"
    _description = "Sequence Option Line"
    _check_company_auto = True

    base_id = fields.Many2one(
        comodel_name="ir.sequence.option",
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
        check_company=True,
    )
    prefix = fields.Char(
        related="sequence_id.prefix",
        string="Prefix",
    )
    suffix = fields.Char(
        related="sequence_id.suffix",
        string="Suffix",
    )
    implementation = fields.Selection(
        related="sequence_id.implementation",
        string="Implementation",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="base_id.company_id",
        store=True,
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
        # multi-company
        company = (
            hasattr(record, "company_id") and record.company_id or self.env.company
        )
        options = options.filtered(lambda x: x.company_id == company)
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
