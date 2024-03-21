# Copyright 2023-2024 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    pending_review_ids = fields.One2many(
        comodel_name="tier.review",
        inverse_name="res_id",
        string="Validations",
        compute="_compute_pending_review_ids",
    )
    total_pending_reviews = fields.Integer(compute="_compute_total_pending_reviews")
    total_pending_reviews_without_changeset = fields.Integer(
        compute="_compute_total_pending_reviews_without_changeset"
    )

    @api.depends("review_ids", "review_ids.status")
    def _compute_pending_review_ids(self):
        for item in self:
            item.pending_review_ids = item.review_ids.filtered(
                lambda x: x.status == "pending" and (self.env.user in x.reviewer_ids)
            )

    @api.depends("pending_review_ids")
    def _compute_total_pending_reviews(self):
        for item in self:
            item.total_pending_reviews = len(item.pending_review_ids)

    @api.depends("pending_review_ids")
    def _compute_total_pending_reviews_without_changeset(self):
        """Get total of pending revisions without changesets.
        We will use this total to keep the base_tier_validation working."""
        for item in self:
            reviews = item.pending_review_ids.filtered(lambda x: not x.changeset_id)
            item.total_pending_reviews_without_changeset = len(reviews)

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
        """Change the behavior so that only the 1st pending revision is validated
        with the _tier_process() method, something similar to what
        base_tier_validation does."""
        self.ensure_one()
        tier_reviews = tiers or self.review_ids
        user_reviews = tier_reviews.filtered(
            lambda r: r.status == "pending" and (self.env.user in r.reviewer_ids)
        )
        user_review = fields.first(user_reviews)
        user_review._tier_process("approved")

    def _rejected_tier(self, tiers=False):
        """Change the behavior so that only the 1st pending revision is rejected
        with the _tier_process() method, something similar to what
        base_tier_validation does."""
        self.ensure_one()
        tier_reviews = tiers or self.review_ids
        user_reviews = tier_reviews.filtered(
            lambda r: r.status == "pending" and (self.env.user in r.reviewer_ids)
        )
        user_review = fields.first(user_reviews)
        user_review._tier_process("rejected")

    def restart_validation(self):
        """Overwrite this method to remove only revisions not linked to changeset."""
        for rec in self:
            if getattr(rec, self._state_field) in self._state_from:
                rec.mapped("review_ids").filtered(lambda x: not x.changeset_id).unlink()
                self._update_counter()
            rec._notify_restarted_review()
