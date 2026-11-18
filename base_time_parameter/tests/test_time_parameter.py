from datetime import date, datetime
from unittest.mock import patch

from lxml import etree
from psycopg2 import IntegrityError

from odoo.exceptions import UserError, ValidationError
from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

WRONG_MODEL = "Value is None because of wrong model"
DONALD_TRUMP = "The value is 'Donald Trump'"
JOE_BIDEN = "The value is 'Joe Biden'"


class TestTimeParameter(TransactionCase):
    def setUp(self):
        super().setUp()

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

    def test_03_company_specific_parameter_wins(self):
        other_company = self.env["res.company"].create({"name": "Other Company"})
        self.env["base.time.parameter"].create(
            {
                "code": "TEST_COMPANY",
                "type": "string",
                "company_id": False,
                "version_ids": [
                    (0, 0, {"date_from": date(2022, 1, 1), "value": "GLOBAL"}),
                ],
            }
        )
        # A global parameter is found by any company.
        value = self.env["res.partner"].get_time_parameter("TEST_COMPANY")
        self.assertEqual(value, "GLOBAL", "The global value is used as a default")

        self.env["base.time.parameter"].create(
            {
                "code": "TEST_COMPANY",
                "type": "string",
                "company_id": self.env.company.id,
                "version_ids": [
                    (0, 0, {"date_from": date(2022, 1, 1), "value": "COMPANY"}),
                ],
            }
        )
        # The parameter of the current company overrides the global one.
        value = self.env["res.partner"].get_time_parameter("TEST_COMPANY")
        self.assertEqual(value, "COMPANY", "The company value overrides the global one")

        # Another company still gets the global value.
        value = (
            self.env["res.partner"]
            .with_company(other_company)
            .get_time_parameter("TEST_COMPANY")
        )
        self.assertEqual(value, "GLOBAL", "Another company keeps the global value")

    def test_04_model_specific_parameter_wins(self):
        self.env["base.time.parameter"].create(
            {
                "code": "TEST_MODEL",
                "type": "string",
                "company_id": False,
                "version_ids": [
                    (0, 0, {"date_from": date(2022, 1, 1), "value": "ANY_MODEL"}),
                ],
            }
        )
        self.env["base.time.parameter"].create(
            {
                "code": "TEST_MODEL",
                "type": "string",
                "company_id": False,
                "model_id": self.env.ref("base.model_res_country").id,
                "version_ids": [
                    (0, 0, {"date_from": date(2022, 1, 1), "value": "COUNTRY"}),
                ],
            }
        )
        value = self.env["res.country"].get_time_parameter("TEST_MODEL")
        self.assertEqual(value, "COUNTRY", "The model specific value is used")
        value = self.env["res.partner"].get_time_parameter("TEST_MODEL")
        self.assertEqual(value, "ANY_MODEL", "Any other model gets the generic value")

    def test_05_raise_if_not_found(self):
        # Not raising is the default, whatever the model.
        value = self.env["res.partner"].get_time_parameter("US President")
        self.assertIsNone(value, WRONG_MODEL)
        # The caller may ask for an error instead.
        with self.assertRaises(UserError):
            self.env["res.partner"].get_time_parameter(
                "US President", raise_if_not_found=True
            )
        # A parameter that is found is returned, not raised about.
        value = self.env["res.country"].get_time_parameter(
            "US President", raise_if_not_found=True
        )
        self.assertEqual(value, "Joe Biden", JOE_BIDEN)

    def test_06_version_value_is_validated(self):
        # A value that the parameter type cannot parse is refused on write,
        # not only in the form view.
        with self.assertRaises(ValidationError):
            self.float_parameter.write(
                {
                    "version_ids": [
                        (0, 0, {"date_from": date(2024, 1, 1), "value": "twelve"})
                    ]
                }
            )
        with self.assertRaises(ValidationError):
            self.env["base.time.parameter"].create(
                {
                    "code": "TEST_BAD_DATE",
                    "type": "date",
                    "version_ids": [
                        (0, 0, {"date_from": date(2022, 1, 1), "value": "31/12/2022"})
                    ],
                }
            )
        with self.assertRaises(ValidationError):
            self.env["base.time.parameter"].create(
                {
                    "code": "TEST_BAD_JSON",
                    "type": "json",
                    "version_ids": [
                        (0, 0, {"date_from": date(2022, 1, 1), "value": "{key: val}"})
                    ],
                }
            )
        # Changing the type of a parameter revalidates its versions.
        with self.assertRaises(ValidationError):
            self.code_string_parameter.type = "integer"
        # Valid values are accepted.
        self.integer_parameter.write(
            {"version_ids": [(0, 0, {"date_from": date(2024, 1, 1), "value": "7"})]}
        )
        self.assertEqual(self.integer_parameter._get(date(2024, 6, 1)), 7)

    def test_07_record_parameter(self):
        # The selection of "value_reference" is empty in this module; a module
        # adding a model to it is simulated here.
        version_field = self.env["base.time.parameter.version"]._fields[
            "value_reference"
        ]
        partner = self.env["res.partner"].create({"name": "Referenced Partner"})
        with patch.object(version_field, "selection", [("res.partner", "Partner")]):
            parameter = self.env["base.time.parameter"].create(
                {
                    "code": "TEST_RECORD",
                    "type": "record",
                    "version_ids": [
                        (
                            0,
                            0,
                            {
                                "date_from": date(2022, 1, 1),
                                "value_reference": f"res.partner,{partner.id}",
                            },
                        )
                    ],
                }
            )
            value = parameter._get(date(2023, 1, 1))
            self.assertEqual(value, partner, "The referenced record is returned")

    def test_08_get_version(self):
        parameter = self.name_string_us_parameter
        self.assertFalse(
            parameter._get_version(date(1999, 1, 1)),
            "No version is in force before the first one starts",
        )
        version = parameter._get_version(date(2018, 1, 1))
        self.assertEqual(version.value, "Donald Trump", DONALD_TRUMP)
        # A version is in force from its very first day.
        version = parameter._get_version(date(2021, 1, 20))
        self.assertEqual(version.value, "Joe Biden", JOE_BIDEN)
        # No date: today.
        self.assertEqual(parameter._get_version().value, "Joe Biden", JOE_BIDEN)

    def test_09_lookup_domain_is_a_hook(self):
        Parameter = self.env["base.time.parameter"]
        model = self.env.ref("base.model_res_country")
        self.assertEqual(
            Parameter.search(Parameter._get_lookup_domain(model, "US President")),
            self.name_string_us_parameter,
        )
        # A parameter with a code is not found by its name.
        self.code_string_parameter.name = "Named"
        self.assertFalse(Parameter.search(Parameter._get_lookup_domain(model, "Named")))

        # A module restricting the domain keeps a parameter out of the lookup.
        def restricted_domain(self, model, code):
            return original_domain(self, model, code) + [("description", "=", False)]

        original_domain = type(Parameter)._get_lookup_domain
        self.name_string_us_parameter.description = "Not part of the lookup"
        with patch.object(type(Parameter), "_get_lookup_domain", restricted_domain):
            value = self.env["res.country"].get_time_parameter("US President")
        self.assertIsNone(value, "The parameter is excluded by the domain")
        value = self.env["res.country"].get_time_parameter("US President")
        self.assertEqual(value, "Joe Biden", JOE_BIDEN)

    def _create_parameter(self, code, value, company=False, kind="float", **vals):
        versions = []
        if value is not False:
            versions = [(0, 0, {"date_from": date(2022, 1, 1), "value": value})]
        return self.env["base.time.parameter"].create(
            {
                "code": code,
                "type": kind,
                "company_id": company and company.id,
                "version_ids": versions,
                **vals,
            }
        )

    def test_10_zero_is_a_value(self):
        # A company sets 0 on purpose: the global default must not come back.
        self._create_parameter("TEST_ZERO", "7.0")
        self._create_parameter("TEST_ZERO", "0.0", company=self.env.company)
        value = self.env["res.partner"].get_time_parameter("TEST_ZERO")
        self.assertEqual(value, 0.0, "The 0 of the company is the value")
        self.assertIsNotNone(value)
        # ... and it is a value for raise_if_not_found too.
        value = self.env["res.partner"].get_time_parameter(
            "TEST_ZERO", raise_if_not_found=True
        )
        self.assertEqual(value, 0.0)

        self._create_parameter("TEST_INT_ZERO", "7", kind="integer")
        self._create_parameter(
            "TEST_INT_ZERO", "0", company=self.env.company, kind="integer"
        )
        value = self.env["res.partner"].get_time_parameter("TEST_INT_ZERO")
        self.assertEqual(value, 0)
        self.assertIsNotNone(value)

    def test_11_false_is_a_value(self):
        self._create_parameter("TEST_FALSE", "True", kind="boolean")
        self._create_parameter(
            "TEST_FALSE", "False", company=self.env.company, kind="boolean"
        )
        value = self.env["res.partner"].get_time_parameter("TEST_FALSE")
        self.assertIs(value, False, "The False of the company is the value")

    def test_12_version_without_value(self):
        # The version in force has no value: the answer is None, the lookup
        # does not go on to the next parameter.
        self._create_parameter("TEST_EMPTY", "7.0")
        company_parameter = self._create_parameter(
            "TEST_EMPTY", "9.0", company=self.env.company
        )
        company_parameter.write(
            {"version_ids": [(0, 0, {"date_from": date(2023, 1, 1), "value": False})]}
        )
        Partner = self.env["res.partner"]
        value = Partner.get_time_parameter("TEST_EMPTY", date(2022, 6, 1))
        self.assertEqual(value, 9.0)
        value = Partner.get_time_parameter("TEST_EMPTY", date(2023, 6, 1))
        self.assertIsNone(value, "The empty version of the company wins")
        # It is not a missing parameter either.
        value = Partner.get_time_parameter(
            "TEST_EMPTY", date(2023, 6, 1), raise_if_not_found=True
        )
        self.assertIsNone(value)
        # The date of that version is still available.
        value = Partner.get_time_parameter("TEST_EMPTY", date(2023, 6, 1), get="date")
        self.assertEqual(value, date(2023, 1, 1))
        # Every type reads an empty version as None.
        for kind in ("boolean", "date", "float", "integer", "json", "string"):
            parameter = self._create_parameter(f"TEST_EMPTY_{kind}", "", kind=kind)
            self.assertIsNone(parameter._get(date(2022, 6, 1)), kind)

    def test_13_parameter_without_version_at_date_is_skipped(self):
        # The parameter of the company only starts in 2030: until then the
        # global one answers.
        self._create_parameter("TEST_LATER", "7.0")
        company_parameter = self._create_parameter(
            "TEST_LATER", False, company=self.env.company
        )
        Partner = self.env["res.partner"]
        value = Partner.get_time_parameter("TEST_LATER", date(2025, 1, 1))
        self.assertEqual(value, 7.0, "A parameter with no version is skipped")
        company_parameter.write(
            {"version_ids": [(0, 0, {"date_from": date(2030, 1, 1), "value": "9.0"})]}
        )
        value = Partner.get_time_parameter("TEST_LATER", date(2025, 1, 1))
        self.assertEqual(value, 7.0, "A version of the future is not in force")
        value = Partner.get_time_parameter("TEST_LATER", date(2030, 1, 1))
        self.assertEqual(value, 9.0)
        # No parameter has a version at that date: not found.
        self.assertIsNone(Partner.get_time_parameter("TEST_LATER", date(2020, 1, 1)))
        with self.assertRaises(UserError):
            Partner.get_time_parameter(
                "TEST_LATER", date(2020, 1, 1), raise_if_not_found=True
            )

    def test_14_lookup_as_regular_user(self):
        # Reading a parameter needs the rights on the parameters, not on
        # ir.model, which a regular user cannot read.
        user = new_test_user(
            self.env,
            login="time_parameter_user",
            groups="base.group_user,base_time_parameter.group_time_parameter",
        )
        self._create_parameter(
            "TEST_USER", "USER", company=self.env.company, kind="string"
        )
        value = self.env["res.partner"].with_user(user).get_time_parameter("TEST_USER")
        self.assertEqual(value, "USER")
        with self.assertRaises(UserError):
            self.env["res.partner"].with_user(user).get_time_parameter(
                "TEST_MISSING", raise_if_not_found=True
            )

    def test_15_company_in_views(self):
        # The company is on the form, so that a multi-company user may give a
        # parameter to another company or make it global; and no view makes
        # it mandatory, the model does not.
        Parameter = self.env["base.time.parameter"]
        self.assertFalse(Parameter._fields["company_id"].required)
        for xmlid in (
            "base_time_parameter.base_time_parameter_view_form",
            "base_time_parameter.base_time_parameter_view_form_hide_model",
            "base_time_parameter.base_time_parameter_view_tree",
        ):
            view = self.env.ref(xmlid)
            arch = etree.fromstring(view.get_combined_arch())
            nodes = arch.xpath("//field[@name='company_id'][not(ancestor::field)]")
            self.assertEqual(len(nodes), 1, xmlid)
            self.assertEqual(nodes[0].get("groups"), "base.group_multi_company")
            self.assertFalse(nodes[0].get("required"), xmlid)

    def test_16_code_is_unique_per_company(self):
        other_company = self.env["res.company"].create({"name": "Other Company"})
        self._create_parameter("TEST_UNIQUE", "1.0", company=self.env.company)
        # Another company may have a parameter with the same code...
        self._create_parameter("TEST_UNIQUE", "2.0", company=other_company)
        # ... but the same company may not have two.
        with self.assertRaises(IntegrityError), mute_logger("odoo.sql_db"):
            self._create_parameter("TEST_UNIQUE", "3.0", company=self.env.company)
