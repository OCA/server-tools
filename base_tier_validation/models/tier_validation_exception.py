# Copyright 2024 Moduon Team (https://www.moduon.team)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, fields, models

from .tier_validation import BASE_EXCEPTION_FIELDS


class TierValidationException(models.Model):
    _name = "tier.validation.exception"
    _description = "Tier Validation Exceptions"

    @api.model
    def _get_tier_validation_model_names(self):
        return self.env["tier.definition"]._get_tier_validation_model_names()

    name = fields.Char(
        required=True,
        default="New Tier Validation Exception",
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Model",
        required=True,
        ondelete="cascade",
        domain=lambda self: [("model", "in", self._get_tier_validation_model_names())],
    )
    model_name = fields.Char(
        related="model_id.model",
        string="Model Name",
        store=True,
        index=True,
    )
    field_ids = fields.Many2many(
        comodel_name="ir.model.fields",
        string="Fields",
        domain="[('id', 'in', valid_model_field_ids)]",
        required=True,
    )
    valid_model_field_ids = fields.One2many(
        comodel_name="ir.model.fields",
        compute="_compute_valid_model_field_ids",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    allowed_to_write_under_validation = fields.Boolean(
        string="Write under Validation",
        default=True,
    )
    allowed_to_write_after_validation = fields.Boolean(
        string="Write after Validation",
        default=True,
    )
    group_ids = fields.Many2many(
        comodel_name="res.groups",
        string="Groups",
        help="Allowed groups to use this Tier Validation Exception",
    )

    @api.depends("model_id")
    def _compute_valid_model_field_ids(self):
        model_names = self.mapped("model_name")
        valid_model_fields = dict(
            self.env["ir.model.fields"]
            .sudo()
            ._read_group(
                domain=[
                    ("model", "in", model_names),
                    ("name", "not in", BASE_EXCEPTION_FIELDS),
                ],
                groupby=["model"],
                aggregates=["id:array_agg"],
            )
        )
        for record in self:
            record.valid_model_field_ids = valid_model_fields.get(record.model_name, [])

    @api.constrains(
        "allowed_to_write_under_validation", "allowed_to_write_after_validation"
    )
    def _check_allowed_to_write(self):
        if (
            not self.allowed_to_write_under_validation
            and not self.allowed_to_write_after_validation
        ):
            raise exceptions.ValidationError(
                self.env._(
                    "At least one of these fields must be checked! "
                    "Write under Validation, Write after Validation"
                )
            )
