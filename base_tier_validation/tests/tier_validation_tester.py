# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TierValidationTester(models.Model):
    _name = "tier.validation.tester"
    _description = "Tier Validation Tester"
    _inherit = ["tier.validation", "mail.thread"]
    _tier_validation_manual_config = True

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("cancel", "Cancel"),
        ],
        default="draft",
    )
    test_validation_field = fields.Integer(default=0)
    test_field = fields.Float()
    user_id = fields.Many2one(string="Assigned to:", comodel_name="res.users")

    def action_confirm(self):
        self.write({"state": "confirmed"})


class TierValidationTester2(models.Model):
    _name = "tier.validation.tester2"
    _description = "Tier Validation Tester 2"
    _inherit = ["tier.validation"]
    _tier_validation_manual_config = False

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("cancel", "Cancel"),
        ],
        default="draft",
    )
    test_field = fields.Float()
    test_validation_field = fields.Float()
    user_id = fields.Many2one(string="Assigned to:", comodel_name="res.users")
    company_id = fields.Many2one(comodel_name="res.company")

    def action_confirm(self):
        self.write({"state": "confirmed"})


class TierValidationTesterComputed(models.Model):
    _name = "tier.validation.tester.computed"
    _description = "Tier Validation Tester Computed"
    _inherit = ["tier.validation"]
    _tier_validation_manual_config = False
    _tier_validation_state_field_is_computed = True

    confirmed = fields.Boolean()
    cancelled = fields.Boolean()
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("cancel", "Cancel"),
        ],
        compute="_compute_state",
        store=True,
    )
    test_field = fields.Float()
    test_validation_field = fields.Float()
    user_id = fields.Many2one(string="Assigned to:", comodel_name="res.users")

    @api.model
    def _get_after_validation_exceptions(self):
        return super()._get_after_validation_exceptions() + [
            "confirmed",
            "cancelled",
        ]

    @api.model
    def _get_under_validation_exceptions(self):
        return super()._get_under_validation_exceptions() + [
            "confirmed",
            "cancelled",
        ]

    @api.depends("confirmed", "cancelled")
    def _compute_state(self):
        for rec in self:
            if rec.cancelled:
                rec.state = "cancel"
            elif rec.confirmed:
                rec.state = "confirmed"
            else:
                rec.state = "draft"

    def action_confirm(self):
        self.write({"confirmed": True})

    def action_cancel(self):
        self.write({"cancelled": True})


class TierDefinition(models.Model):
    _inherit = "tier.definition"

    @api.model
    def _get_tier_validation_model_names(self):
        res = super()._get_tier_validation_model_names()
        res.append("tier.validation.tester")
        res.append("tier.validation.tester2")
        res.append("tier.validation.tester.computed")
        return res
