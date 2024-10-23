import base64

from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import Form, TransactionCase


class BigQueryCase(TransactionCase):
    def test_ensure_client(self):
        with self.assertRaisesRegex(Exception, r"Use `authenticate\(\)` first"):
            self.env["google.bigquery"]._ensure_client()
        with self.assertRaises(UserError):
            self.env["google.bigquery"].authenticate()

    def test_onboarding(self):
        company = self.env["res.company"].create({"name": "Company X"})
        company.bigquery_credentials = base64.b64encode(b'{"project_id": "project"}')
        company._compute_bigquery_project()
        self.assertEqual(
            company.bigquery_onboarding_step_credentials_state, "just_done"
        )
        self.env["ir.model.bigquery"].create(
            {
                "model_id": self.ref("google_bigquery.model_google_bigquery_location"),
                "company_id": company.id,
                "enabled": True,
            }
        )
        self.assertEqual(company.bigquery_onboarding_step_models_state, "just_done")

        with self.assertRaises(ValidationError):
            company.bigquery_dataset = "a" * 1200
        with self.assertRaises(ValidationError):
            company.bigquery_dataset = "a-1"

    def _create_bigquery_model(self):
        with Form(self.env["ir.model.bigquery"]) as form:
            form.model_id = self.env.ref("base.model_res_partner")
            model = form.save()

        model.field_bigquery_ids.filtered(
            lambda l: l.field_id.name == "state_id"
        ).write(
            {
                "nested": True,
                "child_ids": [
                    Command.create(
                        {"field_id": self.ref("base.field_res_country_state__name")}
                    )
                ],
            }
        )
        model.field_bigquery_ids.filtered(
            lambda l: l.field_id.name == "bank_ids"
        ).write(
            {
                "nested": True,
                "child_ids": [
                    Command.create(
                        {
                            "field_id": self.ref(
                                "base.field_res_partner_bank__acc_number"
                            )
                        }
                    ),
                    Command.create(
                        {
                            "field_id": self.ref(
                                "base.field_res_partner_bank__bank_id"
                            ),
                            "nested": True,
                            "child_ids": [
                                Command.create(
                                    {"field_id": self.ref("base.field_res_bank__name")}
                                )
                            ],
                        }
                    ),
                ],
            }
        )
        return model

    def test_creating_bigquery_definition(self):
        model = self._create_bigquery_model()
        definition = model.to_bigquery_definition()
        definition_state_id = list(filter(lambda f: f.name == "state_id", definition))[
            0
        ]
        self.assertEqual(definition_state_id.field_type, "STRUCT")
        self.assertEqual(definition_state_id.mode, "NULLABLE")
        self.assertEqual(len(definition_state_id.fields), 1)

        definition_bank_ids = list(filter(lambda f: f.name == "bank_ids", definition))[
            0
        ]
        self.assertEqual(definition_bank_ids.field_type, "STRUCT")
        self.assertEqual(definition_bank_ids.mode, "REPEATED")
        self.assertEqual(len(definition_bank_ids.fields), 2)

        recursive_nested_field = list(
            filter(lambda f: f.name == "bank_id", definition_bank_ids.fields)
        )[0]
        self.assertEqual(recursive_nested_field.field_type, "STRUCT")

    def test_converting_records(self):
        model = self._create_bigquery_model()
        record = self.env["res.partner"].create(
            {
                "name": "Partner X",
                "is_company": True,
                "state_id": self.ref("base.state_cl_01"),
                "bank_ids": [Command.create({"acc_number": "1234567890"})],
            }
        )
        converted_record = model.convert_record(record)
        self.assertEqual(type(converted_record["state_id"]), dict)
        self.assertEqual(type(converted_record["bank_ids"]), list)
        self.assertEqual(converted_record["bank_ids"][0]["bank_id"], None)

    def test_toggling(self):
        model = self._create_bigquery_model()
        self.assertFalse(model.enabled)
        model.toggle_enabled()
        self.assertTrue(model.enabled)
        self.assertTrue(model.all_fields_enabled)
        model.toggle_enabled_fields()
        self.assertFalse(model.all_fields_enabled)
        model.field_bigquery_ids.toggle_enabled()
        self.assertTrue(model.field_bigquery_ids[0].enabled)
        model.field_bigquery_ids[0].toggle_nested()
        self.assertTrue(model.field_bigquery_ids[0].nested)
