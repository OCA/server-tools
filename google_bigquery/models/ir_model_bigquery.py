from google.cloud import bigquery

from odoo import api, fields, models


class IrModelBigQuery(models.Model):
    _name = "ir.model.bigquery"
    _inherit = ["mail.thread"]
    _description = "Model BigQuery Settings"
    _rec_name = "display_name"

    model_id = fields.Many2one(
        comodel_name="ir.model",
        ondelete="cascade",
        required=True,
        domain="[('transient', '=', False)]",
    )
    model_name = fields.Char(related="model_id.model")
    display_name = fields.Char(compute="_compute_display_name", store=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    enabled = fields.Boolean(help="Synchronize to BigQuery")
    domain = fields.Text(default="[]", required=True)
    field_bigquery_ids = fields.One2many(
        comodel_name="ir.model.fields.bigquery", inverse_name="model_bigquery_id"
    )
    all_fields_enabled = fields.Boolean(
        compute="_compute_all_fields_enabled", store=True
    )
    batch_size = fields.Integer(default=100)

    _sql_constraints = [
        (
            "company_field_uniq",
            "unique(company_id, model_id)",
            "There's already a BigQuery configuration for this model.",
        )
    ]

    @api.depends("field_bigquery_ids.enabled", "field_bigquery_ids")
    def _compute_all_fields_enabled(self):
        for record in self:
            enabled_fields = record.field_bigquery_ids.filtered(lambda f: f.enabled)
            record.all_fields_enabled = len(enabled_fields) == len(
                record.field_bigquery_ids
            )

    @api.depends("model_id", "model_id.name")
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.model_id.name

    def toggle_enabled(self):
        for record in self:
            record.enabled = not record.enabled

    def toggle_enabled_fields(self):
        for record in self:
            record.field_bigquery_ids.enabled = not record.all_fields_enabled

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if "enabled" in vals and vals["enabled"]:
            res.company_id.set_onboarding_step_done(
                "bigquery_onboarding_step_models_state"
            )
        return res

    def write(self, vals):
        res = super().write(vals)
        if self.filtered(lambda m: m.enabled):
            self.env.company.set_onboarding_step_done(
                "bigquery_onboarding_step_models_state"
            )
        return res

    @api.onchange("model_id")
    def _onchange_model_id(self):
        for record in self:
            if record.model_id:
                record.field_bigquery_ids = [(5, 0, 0)] + [
                    (0, 0, {"field_id": field.id}) for field in record.model_id.field_id
                ]
            else:
                record.field_bigquery_ids = [(5, 0, 0)]

    def to_bigquery_definition(self):
        self.ensure_one()
        schema = []
        enabled_fields = self.field_bigquery_ids.filtered(
            lambda f: f.enabled and f.field_id.name != "id"
        )
        schema.append(bigquery.SchemaField("id", "INTEGER", mode="REQUIRED"))
        schema += enabled_fields.to_bigquery_definition()
        return schema

    def convert_record(self, record):
        self.ensure_one()
        result = dict(
            {"id": record.id},
            **self.field_bigquery_ids.filtered(
                lambda f: f.enabled and f.field_id.name != "id"
            ).convert_record(record)
        )
        return result
