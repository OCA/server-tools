from datetime import date

from odoo.tests.common import TransactionCase

WRONG_MODEL = "Value is None because of wrong model"
JOE_BIDEN = "The value is partner 'Joe Biden'"


class TestTimeParameter(TransactionCase):
    def setUp(self):
        super(TestTimeParameter, self).setUp()

        self.partner2017 = self.env["res.partner"].create({"name": "Donald Trump"})
        self.partner2021 = self.env["res.partner"].create({"name": "Joe Biden"})
        self.code_text_parameter = self.env["base.time.parameter"].create(
            {
                "code": "TEST_CODE",
                "type": "text",
                "version_ids": [
                    (0, 0, {"date_from": date(2022, 1, 1), "value_text": "TEST_VALUE"})
                ],
            }
        )
        version2017 = {
            "date_from": date(2017, 1, 20),
            "value_reference": "res.partner,{}".format(self.partner2017.id),
        }
        version2021 = {
            "date_from": date(2021, 1, 20),
            "value_reference": "res.partner,{}".format(self.partner2021.id),
        }
        self.name_reference_parameter = (
            self.env["base.time.parameter"]
            .with_context(selection_models=["res.partner"])
            .create(
                {
                    "name": "US President",
                    "type": "reference",
                    "model_id": self.env.ref("base.model_res_country").id,
                    "version_ids": [(0, 0, version2017), (0, 0, version2021)],
                }
            )
        )

    def test_00_get_value(self):
        value = self.code_text_parameter._get_value(date(1999, 1, 1))
        self.assertIsNone(value, "The value is None")

        value = self.code_text_parameter._get_value()  # date=now()
        self.assertEqual(value, "TEST_VALUE", "The value is 'TEST_VALUE'")

        value = self.name_reference_parameter._get_value(date(2023, 1, 1))
        self.assertEqual(value, self.partner2021, JOE_BIDEN)

    def test_01_get_value_from_model_code_date(self):
        value = self.env["base.time.parameter"]._get_value_from_model_code_date(
            "res.partner", "US President", raise_if_not_found=False
        )
        self.assertIsNone(value, WRONG_MODEL)

        value = self.env["base.time.parameter"]._get_value_from_model_code_date(
            "res.country", "US President", raise_if_not_found=False
        )
        self.assertEqual(value, self.partner2021, JOE_BIDEN)

    def test_02_base_get_time_parameter(self):
        value = self.env["res.partner"].get_time_parameter(
            "US President", raise_if_not_found=False
        )
        self.assertIsNone(value, WRONG_MODEL)

        value = self.env["res.country"].get_time_parameter(
            "US President", raise_if_not_found=False
        )
        self.assertEqual(value, self.partner2021, JOE_BIDEN)
