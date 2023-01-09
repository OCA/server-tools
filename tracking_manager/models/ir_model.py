# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ast import literal_eval

from odoo import api, fields, models


class IrModel(models.Model):
    _inherit = "ir.model"

    active_custom_tracking = fields.Boolean(default=False)
    tracked_field_count = fields.Integer(compute="_compute_tracked_field_count")
    automatic_custom_tracking = fields.Boolean(
        compute="_compute_automatic_custom_tracking",
        readonly=False,
        store=True,
        default=False,
        help=("If tick new field will be automatically tracked " "if the domain match"),
    )
    automatic_custom_tracking_domain = fields.Char(
        compute="_compute_automatic_custom_tracking_domain",
        store=True,
        readonly=False,
    )

    @api.depends("active_custom_tracking")
    def _compute_automatic_custom_tracking(self):
        for record in self:
            record.automatic_custom_tracking = False

    def _default_automatic_custom_tracking_domain_rules(self):
        return {
            "product.product": [
                "|",
                ("ttype", "!=", "one2many"),
                ("name", "in", ["barcode_ids"]),
            ],
            "sale.order": [
                "|",
                ("ttype", "!=", "one2many"),
                ("name", "in", ["line_ids"]),
            ],
            "account.move": [
                "|",
                ("ttype", "!=", "one2many"),
                ("name", "in", ["invoice_line_ids"]),
            ],
            "default_automatic_rule": [("ttype", "!=", "one2many")],
        }

    @api.depends("automatic_custom_tracking")
    def _compute_automatic_custom_tracking_domain(self):
        rules = self._default_automatic_custom_tracking_domain_rules()
        for record in self:
            record.automatic_custom_tracking_domain = str(
                rules.get(record.model) or rules.get("default_automatic_rule")
            )

    def update_custom_tracking(self):
        for record in self:
            fields = record.field_id.filtered("trackable").filtered_domain(
                literal_eval(record.automatic_custom_tracking_domain)
            )
            fields.write({"custom_tracking": True})
            untrack_fields = record.field_id - fields
            untrack_fields.write({"custom_tracking": False})

    @api.depends("field_id.custom_tracking")
    def _compute_tracked_field_count(self):
        for rec in self:
            rec.tracked_field_count = len(rec.field_id.filtered("custom_tracking"))


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

    @api.depends("readonly", "related", "store")
    def _compute_trackable(self):
        blacklists = [
            "activity_ids",
            "message_ids",
            "message_last_post",
            "message_main_attachment",
        ]
        for rec in self:
            rec.trackable = (
                rec.name not in blacklists
                and rec.store
                and not rec.readonly
                and not rec.related
            )

    def write(self, vals):
        custom_tracking = None
        if "custom_tracking" in vals:
            self.check_access_rights("write")
            custom_tracking = vals.pop("custom_tracking")
            self._write({"custom_tracking": custom_tracking})
            self.invalidate_cache(["custom_tracking"])
        return super().write(vals)
