# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ast import literal_eval

from odoo import api, fields, models


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"

    custom_tracking = fields.Boolean(
        compute="_compute_custom_tracking",
        store=True,
        readonly=False,
    )
    native_tracking = fields.Boolean(
        compute="_compute_native_tracking",
        store=True,
    )
    trackable = fields.Boolean(
        compute="_compute_trackable",
        store=True,
    )

    tracking_domain = fields.Char(
        help="Add a domain filter to only track changes when"
        " certain condition apply on the parent record."
    )

    @api.depends("native_tracking")
    def _compute_custom_tracking(self):
        for record in self:
            if record.model_id.automatic_custom_tracking:
                domain = literal_eval(record.model_id.automatic_custom_tracking_domain)
                record.custom_tracking = bool(record.filtered_domain(domain))
            else:
                record.custom_tracking = record.native_tracking

    @api.depends("tracking")
    def _compute_native_tracking(self):
        for record in self:
            record.native_tracking = bool(record.tracking)

    @api.depends("related", "store")
    def _compute_trackable(self):
        blacklists = [
            "activity_ids",
            "message_ids",
            "message_last_post",
            "message_main_attachment",
            "message_main_attachement_id",
        ]

        for rec in self:
            rec.trackable = rec.name not in blacklists and rec.store and not rec.related

    def write(self, vals):
        custom_tracking = None
        if "custom_tracking" in vals:
            self.env.registry.clear_cache()
            self.check_access_rights("write")
            custom_tracking = vals.pop("custom_tracking")
            self._write({"custom_tracking": custom_tracking})
            self.invalidate_model(fnames=["custom_tracking"])
        if "tracking_domain" in vals:
            self.env.registry.clear_cache()
            self.check_access_rights("write")
            custom_tracking_domain = vals.pop("tracking_domain")
            self._write({"tracking_domain": custom_tracking_domain})
            self.invalidate_model(fnames=["tracking_domain"])
        return super().write(vals)
