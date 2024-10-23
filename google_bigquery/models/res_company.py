import base64
import json
import re

from google.api_core.exceptions import BadRequest

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

from odoo.addons.queue_job.delay import chain


class ResCompany(models.Model):
    _name = "res.company"
    _inherit = ["res.company", "google.bigquery.onboarding.mixin"]

    bigquery_credentials = fields.Binary(
        string="BigQuery Credentials",
    )
    bigquery_dataset = fields.Char(string="BigQuery Dataset ID")
    bigquery_dataset_location_id = fields.Many2one(
        string="BigQuery Dataset Location", comodel_name="google.bigquery.location"
    )

    bigquery_project = fields.Char(
        string="BigQuery Project ID", compute="_compute_bigquery_project", store=True
    )
    bigquery_full_name = fields.Char(
        compute="_compute_bigquery_full_name",
        help="Project ID and dataset ID concatenated by a `.`",
        store=True,
    )
    bigquery_sandbox = fields.Boolean(string="Sandbox mode")

    @api.depends("bigquery_project", "bigquery_dataset")
    def _compute_bigquery_full_name(self):
        for company in self:
            company.bigquery_full_name = "%s.%s" % (
                company.bigquery_project,
                company.bigquery_dataset,
            )

    @api.constrains("bigquery_dataset")
    def _constrain_bigquery_dataset(self):
        for company in self.filtered(lambda m: m.bigquery_project):
            if len(company.bigquery_full_name) > 1024:
                raise ValidationError(
                    _("Dataset ID can't be longer than 1024 characters.")
                )
            if not re.match(r"^[0-9a-zA-Z_]+$", company.bigquery_dataset):
                raise ValidationError(
                    _("Dataset ID can only contain letters numbers and underscores.")
                )

    @api.depends("bigquery_credentials")
    def _compute_bigquery_project(self):
        for company in self:
            company.bigquery_project = False
            if company.bigquery_credentials:
                try:
                    parsed_credentials = json.loads(
                        base64.b64decode(company.bigquery_credentials)
                    )
                    company.bigquery_project = parsed_credentials["project_id"]
                    company.set_onboarding_step_done(
                        "bigquery_onboarding_step_credentials_state"
                    )
                except UnicodeDecodeError as ex:
                    raise ValidationError(
                        _("Invalid credentials file, make sure it's JSON formatted")
                    ) from ex

    @api.model
    def _sync_model_to_bigquery(self, bigquery, model, batch_size):
        table_id = model.model_name.replace(".", "_")
        schema = model.to_bigquery_definition()
        bigquery.ensure_table(table_id, schema, friendly_name=model.model_id.name)
        domain = safe_eval(model.domain)

        count = self.env[model.model_name].search(domain, count=True)
        if not count:
            return
        batches = range(0, count, batch_size)
        append = False
        jobs = []
        for batch in batches:
            job = self.delayable()._sync_batch_to_bigquery(
                model.id, domain, batch, batch_size, append
            )
            if not append:
                append = True
            jobs.append(job)
        chain(*jobs).delay()

    @api.model
    def _sync_batch_to_bigquery(self, model_id, domain, offset, limit, append=False):
        model = self.env["ir.model.bigquery"].browse(model_id)
        bigquery = self.env["google.bigquery"].authenticate()
        table_id = model.model_name.replace(".", "_")
        schema = model.to_bigquery_definition()
        records = self.env[model.model_name].search(domain, offset=offset, limit=limit)
        converted_records = []
        for record in records:
            converted_records.append(model.convert_record(record))
        records.invalidate_cache(ids=records.ids)

        # https://cloud.google.com/bigquery/pricing#free
        job = bigquery.load_list(table_id, schema, converted_records, append)
        try:
            job.result()
        except BadRequest as ex:
            error = "\r\n".join(map(lambda e: e["message"], job.errors))
            raise Exception(error) from ex

    @api.model
    def _cron_sync_to_bigquery(self):
        companies = self.search(
            [("bigquery_project", "!=", False), ("bigquery_dataset", "!=", False)]
        )

        for company in companies:
            self = self.with_company(company)
            bigquery = self.env["google.bigquery"].authenticate()
            bigquery.ensure_dataset()

            models = self.env["ir.model.bigquery"].search([("enabled", "=", True)])
            for model in models:
                self._sync_model_to_bigquery(bigquery, model, model.batch_size)
