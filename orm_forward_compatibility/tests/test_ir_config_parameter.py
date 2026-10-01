# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).
from odoo.tests.common import TransactionCase

KEY = "orm_forward_compatibility.test_key"
MISSING_KEY = "orm_forward_compatibility.missing_key"


class TestIrConfigParameter(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.params = cls.env["ir.config_parameter"].sudo()

    def _set(self, value):
        self.params.set_param(KEY, value)

    def test_get_str(self):
        self._set("hello")
        self.assertEqual(self.params.get_str(KEY), "hello")

    def test_get_str_casts_to_str(self):
        self._set(42)
        self.assertEqual(self.params.get_str(KEY), "42")

    def test_get_str_missing_key(self):
        self.assertEqual(self.params.get_str(MISSING_KEY), "")
        self.assertEqual(self.params.get_str(MISSING_KEY, "fallback"), "fallback")

    def test_get_int(self):
        self._set("5")
        self.assertEqual(self.params.get_int(KEY), 5)

    def test_get_int_missing_key(self):
        self.assertEqual(self.params.get_int(MISSING_KEY), 0)
        self.assertEqual(self.params.get_int(MISSING_KEY, 20), 20)

    def test_get_int_unparsable_value_falls_back(self):
        # A hand-edited parameter must not break the caller.
        self._set("not-a-number")
        self.assertEqual(self.params.get_int(KEY, 20), 20)

    def test_get_float(self):
        self._set("1.5")
        self.assertEqual(self.params.get_float(KEY), 1.5)

    def test_get_float_missing_key(self):
        self.assertEqual(self.params.get_float(MISSING_KEY), 0.0)
        self.assertEqual(self.params.get_float(MISSING_KEY, 2.5), 2.5)

    def test_get_float_unparsable_value_falls_back(self):
        self._set("not-a-number")
        self.assertEqual(self.params.get_float(KEY, 2.5), 2.5)

    def test_get_bool(self):
        for value, expected in [
            ("1", True),
            ("True", True),
            ("yes", True),
            ("0", False),
            ("False", False),
            ("off", False),
        ]:
            with self.subTest(value=value):
                self._set(value)
                self.assertIs(self.params.get_bool(KEY), expected)

    def test_get_bool_missing_key(self):
        self.assertIs(self.params.get_bool(MISSING_KEY), False)
        self.assertIs(self.params.get_bool(MISSING_KEY, True), True)

    def test_get_bool_unparsable_value_falls_back(self):
        self._set("maybe")
        self.assertIs(self.params.get_bool(KEY, True), True)
        self.assertIs(self.params.get_bool(KEY, False), False)
