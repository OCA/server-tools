# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ast import literal_eval

from odoo import api, fields, models, tools


class IrModel(models.Model):
    _inherit = "ir.model"

    active_custom_tracking = fields.Boolean()
    tracked_field_count = fields.Integer(compute="_compute_tracked_field_count")
    automatic_custom_tracking = fields.Boolean(
        compute="_compute_automatic_custom_tracking",
        readonly=False,
        store=True,
        help=("If tick new field will be automatically tracked if the domain match"),
    )
    automatic_custom_tracking_domain = fields.Char(
        compute="_compute_automatic_custom_tracking_domain",
        store=True,
        readonly=False,
    )

    @tools.ormcache()
    def _get_custom_tracked_fields_per_model(self):
        models = self.sudo().search([("active_custom_tracking", "=", True)])
        return {
            model.model: model.field_id.filtered(
                lambda f: f.custom_tracking
                and self.env[model.model]._fields.get(f.name)
            ).mapped("name")
            for model in models
            if model.model in self.env
        }

    @tools.ormcache()
    def _get_model_tracked_by_o2m(self):
        """For each model tracked due to a o2m relation
        compute the information of
        - the fields to track
        - the 'notify" field to found the related record to post the message
        return example
        {
            "res.partner.bank": {
                "fields": ["acc_holder_name", "acc_number", ...],
                "notify": [["partner_id", "bank_ids"]],
            }
        }
        """
        self = self.sudo()
        fields = self.env["ir.model.fields"].search(
            [
                ("custom_tracking", "=", True),
                ("model_id.active_custom_tracking", "=", True),
                ("ttype", "=", "one2many"),
            ]
        )
        related_models = self.env["ir.model"].search(
            [
                ("model", "in", fields.mapped("relation")),
            ]
        )
        custom_tracked_fields = self._get_custom_tracked_fields_per_model()
        res = {}
        for model in related_models:
            if model.model not in self.env:
                # If the model do not exist skip it (ex: during module update)
                continue
            if model.model in custom_tracked_fields:
                tracked_fields = custom_tracked_fields[model.model]
            else:
                tracked_fields = model.field_id.filtered(
                    lambda s: not s.readonly
                    and not s.related
                    and not s.ttype == "one2many"
                    and s.name in self.env[model.model]._fields
                ).mapped("name")
            res[model.model] = {"fields": tracked_fields, "notify": []}

        for field in fields:
            model_name = field.model_id.model
            if (
                model_name in self.env
                and self.env[model_name]._fields.get(field.name)
                and field.relation in res
            ):
                res[field.relation]["notify"].append(
                    [self.env[model_name]._fields[field.name].inverse_name, field.name]
                )
        return res

    @api.depends("active_custom_tracking")
    def _compute_automatic_custom_tracking(self):
        for record in self:
            record.automatic_custom_tracking = False

    def _default_automatic_custom_tracking_domain_rules(self):
        return {
            "product.product": [
                ("readonly", "=", False),
                "|",
                ("ttype", "!=", "one2many"),
                ("name", "in", ["barcode_ids"]),
            ],
            "sale.order": [
                ("readonly", "=", False),
                "|",
                ("ttype", "!=", "one2many"),
                ("name", "in", ["order_line"]),
            ],
            "account.move": [
                ("readonly", "=", False),
                "|",
                ("ttype", "!=", "one2many"),
                ("name", "in", ["invoice_line_ids"]),
            ],
            "default_automatic_rule": [
                ("ttype", "!=", "one2many"),
                ("readonly", "=", False),
            ],
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

    def write(self, vals):
        if "active_custom_tracking" in vals:
            self.clear_caches()
        return super().write(vals)


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
            self.clear_caches()
            self.check_access_rights("write")
            custom_tracking = vals.pop("custom_tracking")
            self._write({"custom_tracking": custom_tracking})
            self.invalidate_model(fnames=["custom_tracking"])
        return super().write(vals)
