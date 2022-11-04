from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    bigquery_credentials = fields.Binary(
        related="company_id.bigquery_credentials", readonly=False
    )
    bigquery_dataset = fields.Char(
        related="company_id.bigquery_dataset", readonly=False
    )
    bigquery_dataset_location_id = fields.Many2one(
        related="company_id.bigquery_dataset_location_id", readonly=False
    )
    bigquery_project = fields.Char(related="company_id.bigquery_project")
    bigquery_sandbox = fields.Boolean(
        related="company_id.bigquery_sandbox", readonly=False
    )
