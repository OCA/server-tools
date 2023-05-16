# Copyright 2023 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class TierReview(models.Model):
    _inherit = "tier.review"

    summary_field_id = fields.Many2one(
        comodel_name="ir.model.fields", compute="_compute_summary_field_id", store=True
    )
    summary = fields.Char(string="Summary", compute="_compute_summary", store=True)
    changeset_id = fields.Many2one(comodel_name="record.changeset")

    @api.depends("definition_id", "changeset_id")
    def _compute_summary_field_id(self):
        for item in self:
            changes = item.changeset_id.change_ids
            if changes and any(x.rule_id.summary_field_id for x in changes):
                final_changes = changes.filtered(lambda x: x.rule_id.summary_field_id)
                change = fields.first(final_changes)
                item.summary_field_id = change.rule_id.summary_field_id
            else:
                item.summary_field_id = item.definition_id.summary_field_id

    @api.depends("summary_field_id", "model", "res_id", "changeset_id")
    def _compute_summary(self):
        for item in self.filtered(lambda x: x.summary_field_id):
            changes = item.changeset_id.change_ids.filtered(
                lambda x: x.field_id == item.summary_field_id
            )
            if changes:
                change = fields.first(changes)
                value = "%s > %s" % (
                    change.origin_value_display,
                    change.new_value_display,
                )
            else:
                field_name = item.summary_field_id.name
                model = self.env[item.model]
                model_field_def = model._fields[field_name]
                record = model.browse(item.res_id)
                value = model_field_def.convert_to_write(record[field_name], record)
            item.summary = "%s: %s" % (item.summary_field_id.field_description, value)

    def _tier_process(self, status):
        """Custom process to accept/reject, similar to _validate_tier()
        and _rejected_tier()."""
        self.ensure_one()
        self.write(
            {
                "status": status,
                "done_by": self.env.user.id,
                "reviewed_date": fields.Datetime.now(),
            }
        )
        rec = self.env[self.model].browse(self.res_id)
        if status == "approved":
            rec._notify_accepted_reviews()
        else:
            rec._notify_rejected_review()
