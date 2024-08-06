import base64
import json

from google.api_core.exceptions import NotFound as GoogleNotFound
from google.cloud import bigquery
from google.oauth2 import service_account

from odoo import _, api, models
from odoo.exceptions import UserError


class GoogleBigQuery(models.AbstractModel):
    _name = "google.bigquery"
    _description = "Google BigQuery"

    @api.model
    def authenticate(self):
        company = self.env.company
        if not company.bigquery_project or not company.bigquery_dataset:
            raise UserError(
                _("Please setup the BigQuery credentials in the general settings.")
            )
        info = json.loads(base64.b64decode(company.bigquery_credentials))
        client = bigquery.Client(
            credentials=service_account.Credentials.from_service_account_info(info)
        )
        return self.with_context(bigquery_client=client)

    def _ensure_client(self):
        client = self.env.context.get("bigquery_client")
        if not client:
            raise Exception("Use `authenticate()` first")
        return client

    def _create_dataset(self, dataset_id, location, exists_ok=False):
        client = self._ensure_client()
        dataset_id = "%s.%s" % (client.project, dataset_id)
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = location
        return client.create_dataset(dataset, exists_ok=exists_ok)

    def ensure_dataset(self):
        company = self.env.company
        return self._create_dataset(
            company.bigquery_dataset,
            company.bigquery_dataset_location_id.name,
            exists_ok=True,
        )

    def _create_table(self, dataset_id, table_id, schema, friendly_name=False):
        client = self._ensure_client()
        self.ensure_dataset()
        table_id = "%s.%s.%s" % (client.project, dataset_id, table_id)
        table = bigquery.Table(table_id, schema=schema)
        if friendly_name:
            table.friendly_name = friendly_name
        return client.create_table(table)

    def _update_table(self, dataset_id, table_id, schema):
        client = self._ensure_client()
        table_id = "%s.%s.%s" % (client.project, dataset_id, table_id)
        table = client.get_table(table_id)
        table.schema = schema
        return client.update_table(table, fields=["schema"])

    def _delete_table(self, dataset_id, table_id):
        client = self._ensure_client()
        table_id = "%s.%s.%s" % (client.project, dataset_id, table_id)
        return client.delete_table(table_id)

    def _table_exists(self, dataset_id, table_id):
        client = self._ensure_client()
        table_id = "%s.%s.%s" % (client.project, dataset_id, table_id)
        try:
            client.get_table(table_id)
            return True
        except GoogleNotFound:
            return False

    def ensure_table(self, table_id, schema, friendly_name=False, recreate=True):
        self.ensure_dataset()
        company = self.env.company
        table_exists = self._table_exists(company.bigquery_dataset, table_id)
        if table_exists and recreate:
            self._delete_table(company.bigquery_dataset, table_id)
        elif table_exists:
            if company.bigquery_sandbox:
                # We can't update tables for some reason without
                # adding a billing plan to Google.
                return None
            return self._update_table(company.bigquery_dataset, table_id, schema)
        return self._create_table(
            company.bigquery_dataset, table_id, schema, friendly_name=friendly_name
        )

    def load_json_file(self, table_id, file_location, append=False):
        client = self._ensure_client()
        company = self.env.company
        table_id = "%s.%s.%s" % (client.project, company.bigquery_dataset, table_id)

        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND
            if append
            else bigquery.WriteDisposition.WRITE_TRUNCATE,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        )

        with open(file_location, "rb") as fh:
            return client.load_table_from_file(
                fh, destination=table_id, job_config=job_config
            )

    def load_list(self, table_id, schema, converted_records, append=False):
        client = self._ensure_client()
        company = self.env.company
        table_id = "%s.%s.%s" % (client.project, company.bigquery_dataset, table_id)

        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND
            if append
            else bigquery.WriteDisposition.WRITE_TRUNCATE,
            schema=schema,
        )
        return client.load_table_from_json(
            converted_records, destination=table_id, job_config=job_config
        )
