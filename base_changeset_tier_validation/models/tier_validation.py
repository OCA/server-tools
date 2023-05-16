# Copyright 2023 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    total_pending_reviews = fields.Integer(compute="_compute_total_pending_reviews")
    last_pending_changeset_review = fields.Many2one(
        comodel_name="record.changeset",
        compute="_compute_last_pending_changeset_review",
    )
    last_pending_changeset_review_ref = fields.Reference(
        selection=lambda self: [
            (model.model, model.name) for model in self.env["ir.model"].search([])
        ],
        compute="_compute_last_pending_changeset_review_ref",
    )

    @api.depends("review_ids.status")
    def _compute_total_pending_reviews(self):
        for item in self:
            item.total_pending_reviews = len(
                item.review_ids.filtered(
                    lambda x: x.status == "pending"
                    and (self.env.user in x.reviewer_ids)
                )
            )

    @api.depends("review_ids.status")
    def _compute_last_pending_changeset_review(self):
        for item in self:
            last_review = fields.first(
                item.review_ids.filtered(
                    lambda x: x.status == "pending" and x.changeset_id
                )
            )
            item.last_pending_changeset_review = last_review.changeset_id

    @api.depends("last_pending_changeset_review")
    def _compute_last_pending_changeset_review_ref(self):
        for item in self:
            if item.last_pending_changeset_review:
                item.last_pending_changeset_review_ref = "%s,%s" % (
                    item.last_pending_changeset_review.model,
                    item.last_pending_changeset_review.res_id,
                )
            else:
                item.last_pending_changeset_review_ref = (
                    item.last_pending_changeset_review_ref
                )

    @api.depends("total_pending_reviews")
    def _compute_need_validation(self):
        """If validation is needed if there is something pending."""
        super()._compute_need_validation()
        for item in self:
            if item.total_pending_reviews > 0:
                item.need_validation = True

    @api.depends("total_pending_reviews")
    def _compute_validated_rejected(self):
        """It is not rejected if there is something pending."""
        super()._compute_validated_rejected()
        for item in self:
            if item.total_pending_reviews > 0:
                item.rejected = False

    def _check_allow_write_under_validation(self, vals):
        """Overwrite to allow multiple revisions if any of them had changeset_id set
        or no review is pending."""
        res = super()._check_allow_write_under_validation(vals=vals)
        if any(x.changeset_id for x in self.review_ids):
            return True
        elif all(x.status != "pending" for x in self.review_ids):
            return True
        return res

    def _validate_tier(self, tiers=False):
        """If you have a changeset_id defined, we want to validate only first pending
        revision and the linked changeset, otherwise the default behavior the linked
        changeset, otherwise the default behavior will be."""
        self.ensure_one()
        tier_reviews = tiers or self.review_ids
        user_reviews = tier_reviews.filtered(
            lambda r: r.status == "pending" and (self.env.user in r.reviewer_ids)
        )
        user_review = fields.first(user_reviews)
        if user_review.changeset_id:
            user_review.changeset_id.apply()
            user_review._tier_process("approved")
        else:
            super()._validate_tier(tiers=tiers)

    def _rejected_tier(self, tiers=False):
        """If you have a changeset_id defined, we want to cancel only first pending
        revision  and the linked changeset, otherwise the default behavior the linked
        changeset, otherwise the default behavior will be."""
        self.ensure_one()
        tier_reviews = tiers or self.review_ids
        user_reviews = tier_reviews.filtered(
            lambda r: r.status == "pending" and (self.env.user in r.reviewer_ids)
        )
        user_review = fields.first(user_reviews)
        if user_review.changeset_id:
            user_review.changeset_id.cancel()
            user_review._tier_process("rejected")
        else:
            super()._rejected_tier(tiers=tiers)
