# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def get_pending_tier_reviews(self, data):
        review_obj = self.env["tier.review"].with_context(lang=self.env.user.lang)
        res = review_obj.search_read(
            [
                ("id", "in", data.get("res_ids")),
                ("status", "=", "pending"),
                ("reviewer_ids", "in", self.env.user.ids),
            ]
        )
        for r in res:
            # Get the translated status value.
            r["display_status"] = dict(
                review_obj.fields_get("status")["status"]["selection"]
            ).get(r.get("status"))
            # Convert to datetime timezone
            if r["reviewed_date"]:
                r["reviewed_date"] = fields.Datetime.context_timestamp(
                    self, r["reviewed_date"]
                )
        return res
