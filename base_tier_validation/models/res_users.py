# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, modules


class Users(models.Model):
    _inherit = "res.users"

    review_ids = fields.Many2many(string="Reviews", comodel_name="tier.review")

    @api.model
    def review_user_count(self):
        user_reviews = {}
        user = self.env.user
        domain = [
            ("status", "=", "pending"),
            ("can_review", "=", True),
            ("id", "in", user.review_ids.ids),
        ]
        review_groups = self.env["tier.review"]._read_group(
            domain=domain,
            groupby=["model"],
            aggregates=["id:recordset"],
        )
        for model, tier_review in review_groups:
            Model = self.env[model]
            # Skip Models not having Tier Validation enabled (example: was unistalled)
            if tier_review and hasattr(Model, "can_review"):
                records_domain = [
                    ("id", "in", tier_review.mapped("res_id")),
                    ("validation_status", "!=", "rejected"),
                    ("can_review", "=", True),
                ]
                records = (
                    Model.with_user(user)
                    .with_context(active_test=False)
                    .search(records_domain)
                )
                # Excludes any cancelled records depending on the structure of the model
                if Model._state_field in Model._fields:
                    records = records.filtered(
                        lambda x: x[x._state_field] != x._cancel_state
                    )
                if records:
                    user_reviews[model] = {
                        "id": records[0].id,
                        "name": Model._description,
                        "model": model,
                        "active_field": "active" in Model._fields,
                        "icon": modules.module.get_module_icon(Model._original_module),
                        "type": "tier_review",
                        "pending_count": len(records),
                    }
        return list(user_reviews.values())
