# Copyright 2023 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class RecordChangesetChange(models.Model):
    _inherit = "record.changeset.change"

    has_review_ids = fields.Boolean(compute="_compute_has_review_ids")

    @api.depends("changeset_id", "changeset_id.review_ids")
    def _compute_has_review_ids(self):
        for item in self:
            item.has_review_ids = bool(item.changeset_id.review_ids)

    def _get_fields_changeset_changes(self):
        """Add an extra field to show or not the change popover buttons."""
        return super()._get_fields_changeset_changes() + ["has_review_ids"]
