# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TrackingModelField(models.Model):
    _name = "tracking.model.field"
    _description = "Tracking Model Field"

    name = fields.Char(related="tracking_field_id.name")
    tracking_field_id = fields.Many2one(
        "ir.model.fields",
        "Field",
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Tracking Model Field",
    )
    custom_tracking = fields.Boolean(
        string="Custom Tracking",
        compute="_compute_custom_tracking",
        readonly=False,
        store=True,
    )
    native_tracking_field = fields.Integer(
        string="Native Tracking", related="tracking_field_id.tracking"
    )
    type_field = fields.Selection(
        string="Kind Field", related="tracking_field_id.ttype"
    )

    @api.depends(
        "tracking_field_id",
        "tracking_field_id.readonly",
        "tracking_field_id.related",
        "tracking_field_id.store",
    )
    def _compute_custom_tracking(self):
        # No tracking on compute / readonly fields
        # Custom tracking include native tracking attribute.
        for rec in self:
            field_id = rec.tracking_field_id
            if (
                field_id.readonly
                or field_id.related
                or (field_id.compute and field_id.store and not field_id.readonly)
            ) and not field_id.tracking:
                rec.custom_tracking = False
            else:
                rec.custom_tracking = True
