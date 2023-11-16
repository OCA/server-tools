# Copyright 2023 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class RecordChangeset(models.Model):
    _inherit = "record.changeset"

    review_summary = fields.Char(
        compute="_compute_review_summary", string="Review Summary", store=True
    )
    review_ids = fields.One2many(
        comodel_name="tier.review",
        inverse_name="changeset_id",
    )

    @api.depends("review_ids", "review_ids.summary")
    def _compute_review_summary(self):
        for item in self:
            review = fields.first(item.review_ids)
            item.review_summary = review.summary if review else False

    @api.model_create_multi
    def create(self, vals_list):
        """If any change rule should create a revision, it is created and processed."""
        result = super().create(vals_list)
        for item in result:
            if any(change.rule_id.create_tier_review for change in item.change_ids) or (
                not item.change_ids and item.action in ("create", "unlink")
            ):
                item._tier_review_process()
        return result

    def _tier_review_process(self):
        review = self.env["tier.review"].create([self._prepare_tier_review_valuess()])
        record = self.env[review.model].browse(review.res_id)
        if hasattr(record, "_notify_review_requested"):
            record._notify_review_requested(review)

    def _prepare_tier_review_valuess(self):
        # set model
        res_id = self.parent_id or self.res_id
        change_0 = fields.first(
            self.change_ids.filtered(lambda x: x.rule_id.create_tier_review)
        )
        changeset_rule = (
            change_0.rule_id if change_0 else self.env.context.get("changeset_rule")
        )
        model = changeset_rule.tier_model or self.parent_model or self.model
        if changeset_rule.tier_parent_field_id:
            record = self.env[model].browse(res_id)
            parent_record = record[changeset_rule.tier_parent_field_id.name]
            res_id = parent_record.id
        # search tier definition
        tier_definition = changeset_rule.tier_definition_id
        total_reviews = self.env["tier.review"].search_count(
            [
                ("model", "=", model),
                ("res_id", "=", res_id),
                ("definition_id", "=", tier_definition.id),
            ]
        )
        return {
            "name": "%s,%s" % (model, res_id),
            "model": model,
            "res_id": res_id,
            "definition_id": tier_definition.id,
            "sequence": total_reviews + 1,
            "requested_by": self.env.uid,
            "changeset_id": self.id,
        }

    def apply(self):
        """Auto-approve related reviews if changeset is apply."""
        super().apply()
        if self.env.context.get("apply_from_changeset"):
            return
        for item in self.filtered(
            lambda x: x.state == "done" and x.review_ids.status == "pending"
        ):
            for review in item.review_ids:
                review.with_context(apply_from_changeset=True)._tier_process("approved")

    def cancel(self):
        """Auto-reject related reviews if changeset is cancel."""
        super().cancel()
        if self.env.context.get("cancel_from_changeset"):
            return

        for item in self.filtered(
            lambda x: x.state == "done" and x.review_ids.status == "pending"
        ):
            for review in item.review_ids:
                review.with_context(cancel_from_changeset=True)._tier_process(
                    "rejected"
                )
