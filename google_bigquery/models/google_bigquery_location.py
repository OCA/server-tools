from odoo import api, fields, models


class GoogleBigQueryLocation(models.Model):
    _name = "google.bigquery.location"
    _description = "Google BigQuery Location"
    _rec_name = "display_name"

    name = fields.Char(required=True)
    description = fields.Char(required=True)
    display_name = fields.Char(compute="_compute_display_name", store=True)

    @api.depends("name", "description")
    def _compute_display_name(self):
        for location in self:
            location.display_name = "%s (%s)" % (location.description, location.name)
