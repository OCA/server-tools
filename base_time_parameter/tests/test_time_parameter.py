from datetime import date, datetime

from odoo.tests.common import TransactionCase

WRONG_MODEL = "Value is None because of wrong model"
DONALD_TRUMP = "The value is 'Donald Trump'"
JOE_BIDEN = "The value is 'Joe Biden'"


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
        self.json_parameter = self.env["base.time.parameter"].create(
            {
                "code": "TEST_JSON",
                "type": "json",
                "version_ids": [
                    (0, 0, {"date_from": date(2022, 1, 1), "value": '{"key": "val"}'}),
                ],
            }
        )
        # testing parameter "code" and "name" together with "string" value
        self.code_string_parameter = self.env["base.time.parameter"].create(
            {
                "code": "TEST_CODE_STRING",
                "type": "string",
                "version_ids": [
                    (0, 0, {"date_from": date(2022, 1, 1), "value": "CODE_STRING"})
                ],
            }
        )
        self.name_string_us_parameter = self.env["base.time.parameter"].create(
            {
                "name": "US President",
                "type": "string",
                "model_id": self.env.ref("base.model_res_country").id,
                "version_ids": [
                    (0, 0, {"date_from": date(2017, 1, 20), "value": "Donald Trump"}),
                    (0, 0, {"date_from": date(2021, 1, 20), "value": "Joe Biden"}),
                ],
            }
        )

    def test_00_get(self):
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

        value = self.json_parameter._get(date(2023, 1, 1))
        self.assertEqual(value, {"key": "val"}, 'Value is json {"key": "val"}')

        # Cannot test reference here, since the selection is an empty list.
        # Reference is tested in account_time_parameter.

        value = self.code_string_parameter._get()  # date=now()
        self.assertEqual(value, "CODE_STRING", "The value is 'CODE_STRING'")

        value = self.name_string_us_parameter._get()  # date=now()
        self.assertEqual(value, "Joe Biden", JOE_BIDEN)

    def test_01_get_from_model_code_date(self):
        value = self.env["base.time.parameter"]._get_from_model_code_date(
            "res.partner", "US President", raise_if_not_found=False
        )
        self.assertIsNone(value, WRONG_MODEL)

        value = self.env["base.time.parameter"]._get_from_model_code_date(
            "res.country", "US President", raise_if_not_found=False
        )
        self.assertEqual(value, "Joe Biden", JOE_BIDEN)

    def test_02_base_get_time_parameter(self):

        # TEST MODEL

        value = self.env["res.partner"].get_time_parameter(
            "US President", raise_if_not_found=False
        )
        self.assertIsNone(value, WRONG_MODEL)

        # TEST DATE

        # no date
        value = self.env["res.country"].get_time_parameter(
            "US President", raise_if_not_found=False
        )
        self.assertEqual(value, "Joe Biden", JOE_BIDEN)
        # date
        value = self.env["res.country"].get_time_parameter(
            "US President", date(2018, 1, 1), raise_if_not_found=False
        )
        self.assertEqual(value, "Donald Trump", DONALD_TRUMP)
        # datetime
        value = self.env["res.country"].get_time_parameter(
            "US President", datetime.now(), raise_if_not_found=False
        )
        self.assertEqual(value, "Joe Biden", JOE_BIDEN)
        # string
        self.env.ref("base.us").name = "UNITED STATES"
        value = self.env.ref("base.us").get_time_parameter(
            "US President", "write_date", raise_if_not_found=False
        )
        self.assertEqual(value, "Joe Biden", JOE_BIDEN)

        # TEST GET

        # get="date"
        date1 = self.env["res.country"].get_time_parameter(
            "TEST_JSON", date(2022, 12, 1), raise_if_not_found=False, get="date"
        )
        self.assertEqual(date1, date(2022, 1, 1), "Start date is Jan. 1, 2022")
        # get="value"
        value = self.env["res.country"].get_time_parameter(
            "TEST_JSON", date(2022, 12, 1), raise_if_not_found=False, get="value"
        )
        self.assertEqual(value, {"key": "val"}, 'Value is json {"key": "val"}')
