# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IrModel(models.Model):
    _inherit = "ir.model"

    o2m_model_ids = fields.One2many(
        string="One2many Models",
        comodel_name="ir.model",
        compute="_compute_o2m_model_ids",
        readonly=True,
    )
    custom_tracking_field_ids = fields.One2many(
        comodel_name="tracking.model.field",
        inverse_name="model_id",
        string="Custom Tracked Fields",
        compute="_compute_custom_tracking_fields",
        store=True,
    )
    field_count = fields.Integer(compute="_compute_tracked_field_count")
    apply_custom_tracking = fields.Boolean(
        "Apply custom tracking on fields",
        default=False,
        help="""Add tracking on all this model fields if they
        are not readonly True, neither computed.""",
    )

    @api.depends("field_id", "apply_custom_tracking")
    def _compute_custom_tracking_fields(self):
        for rec in self:
            fields = rec.env["ir.model.fields"].search(
                [("model_id.model", "=", rec.model)]
            )
            fields_ids = []
            for field in fields:
                values = {}
                values["tracking_field_id"] = field.id
                values["model_id"] = rec.id
                fields_ids.append((0, 0, values))
            rec.custom_tracking_field_ids = [(6, 0, [])]
            rec.custom_tracking_field_ids = fields_ids

    @api.depends("field_id", "apply_custom_tracking")
    def _compute_o2m_model_ids(self):
        for rec in self:
            o2m_model_list = []
            if rec.apply_custom_tracking:
                for field in rec.field_id:
                    if field.ttype == "one2many":
                        o2m_relation_id = self.search(
                            [("model", "=", field.relation)], limit=1
                        )
                        o2m_model_list.append(o2m_relation_id.id)
            rec.o2m_model_ids = [(6, 0, o2m_model_list)]

    @api.depends(
        "custom_tracking_field_ids", "custom_tracking_field_ids.custom_tracking"
    )
    def _compute_tracked_field_count(self):
        for rec in self:
            rec.field_count = sum(
                rec.custom_tracking_field_ids.mapped("custom_tracking")
            )

    def show_custom_tracked_field(self):
        return {
            "name": "Custom tracked fields",
            "type": "ir.actions.act_window",
            "res_id": self.id,
            "view_mode": "tree",
            "res_model": "tracking.model.field",
            "view_id": self.env.ref(
                "tracking_manager.custom_tracking_field_view_tree"
            ).id,
            "target": "current",
            "domain": [("id", "in", self.custom_tracking_field_ids.ids)],
        }

    def show_o2m_models(self):
        return {
            "name": "o2m models",
            "type": "ir.actions.act_window",
            "res_id": self.id,
            "view_mode": "tree,form",
            "res_model": "ir.model",
            "views": [
                (self.env.ref("base.view_model_tree").id, "tree"),
                (self.env.ref("base.view_model_form").id, "form"),
            ],
            "target": "current",
            "domain": [("id", "in", self.o2m_model_ids.ids)],
        }


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"

    custom_tracking_id = fields.Many2one(
        comodel_name="tracking.model.field",
        string="Technical Custom Tracking Field",
        compute="_compute_custom_tracking_field_id",
    )

    @api.depends("model_id.apply_custom_tracking")
    def _compute_custom_tracking_field_id(self):
        for rec in self:
            if rec.model_id.apply_custom_tracking:
                rec.custom_tracking_id = self.env["tracking.model.field"].search(
                    [("tracking_field_id", "=", rec.id), ("model_id", "=", rec._name)],
                    limit=1,
                )
            else:
                rec.custom_tracking_id = False
