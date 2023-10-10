from datetime import date, datetime

from odoo.tests.common import TransactionCase

WRONG_MODEL = "Value is None because of wrong model"
DONALD_TRUMP = "The value is partner 'Donald Trump'"
JOE_BIDEN = "The value is partner 'Joe Biden'"


class TestTimeParameter(TransactionCase):
    def setUp(self):
        super(TestTimeParameter, self).setUp()

        self.boolean_parameter = self.env["base.time.parameter"].create(
            {
                "code": "TEST_BOOLEAN",
                "type": "boolean",
                "version_ids": [
                    (0, 0, {"date_from": date(2022, 1, 1), "value": "True"}),
                    (0, 0, {"date_from": date(2023, 1, 1), "value": "False"}),
                ],
            }
        )
        self.date_parameter = self.env["base.time.parameter"].create(
            {
                "code": "TEST_DATE",
                "type": "date",
                "version_ids": [
                    (0, 0, {"date_from": date(2022, 1, 1), "value": "2022-12-31"}),
                ],
            }
        )
        self.float_parameter = self.env["base.time.parameter"].create(
            {
                "code": "TEST_FLOAT",
                "type": "float",
                "version_ids": [
                    (0, 0, {"date_from": date(2022, 1, 1), "value": "-12.5"}),
                ],
            }
        )
        self.integer_parameter = self.env["base.time.parameter"].create(
            {
                "code": "TEST_INTEGER",
                "type": "integer",
                "version_ids": [
                    (0, 0, {"date_from": date(2022, 1, 1), "value": "123"}),
                ],
            }
        )
        # testing "code" and "name" together with "reference" and "string"
        self.partner2017 = self.env["res.partner"].create({"name": "Donald Trump"})
        self.partner2021 = self.env["res.partner"].create({"name": "Joe Biden"})
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
        self.code_string_parameter = self.env["base.time.parameter"].create(
            {
                "code": "TEST_CODE_STRING",
                "type": "string",
                "version_ids": [
                    (0, 0, {"date_from": date(2022, 1, 1), "value": "TEST_STRING"})
                ],
            }
        )

    def test_00_get_value(self):
        value = self.boolean_parameter._get(date(1999, 1, 1))
        self.assertEqual(value, False, "The value is False")

        value = self.boolean_parameter._get(date(2022, 12, 1))
        self.assertEqual(value, True, "Value is boolean True")
        value = self.boolean_parameter._get(date(2023, 12, 1))
        self.assertEqual(value, False, "Value is boolean False")

        value = self.date_parameter._get(date(2023, 1, 1))
        self.assertEqual(value, date(2022, 12, 31), "Value is the date Dec. 31, 2022")

        value = self.float_parameter._get(date(2023, 1, 1))
        self.assertEqual(value, -12.5, "Value is float -12.5")

        value = self.integer_parameter._get(date(2023, 1, 1))
        self.assertEqual(value, 123, "Value is integer 123")

        value = self.name_reference_parameter._get(date(2023, 1, 1))
        self.assertEqual(value, self.partner2021, JOE_BIDEN)

        value = self.code_string_parameter._get()  # date=now()
        self.assertEqual(value, "TEST_STRING", "The value is 'TEST_STRING'")

    def test_01_get_value_from_model_code_date(self):
        value = self.env["base.time.parameter"]._get_from_model_code_date(
            "res.partner", "US President", raise_if_not_found=False
        )
        self.assertIsNone(value, WRONG_MODEL)

        value = self.env["base.time.parameter"]._get_from_model_code_date(
            "res.country", "US President", raise_if_not_found=False
        )
        self.assertEqual(value, self.partner2021, JOE_BIDEN)

    def test_02_base_get_time_parameter(self):
        value = self.env["res.partner"].get_time_parameter(
            "US President", raise_if_not_found=False
        )
        self.assertIsNone(value, WRONG_MODEL)

        # no date
        value = self.env["res.country"].get_time_parameter(
            "US President", raise_if_not_found=False
        )
        self.assertEqual(value, self.partner2021, JOE_BIDEN)
        # date
        value = self.env["res.country"].get_time_parameter(
            "US President", date(2018, 1, 1), raise_if_not_found=False
        )
        self.assertEqual(value, self.partner2017, DONALD_TRUMP)
        # datetime
        value = self.env["res.country"].get_time_parameter(
            "US President", datetime.now(), raise_if_not_found=False
        )
        self.assertEqual(value, self.partner2021, JOE_BIDEN)
        # string
        self.env.ref("base.us").name = "UNITED STATES"
        value = self.env.ref("base.us").get_time_parameter(
            "US President", "write_date", raise_if_not_found=False
        )
        self.assertEqual(value, self.partner2021, JOE_BIDEN)
