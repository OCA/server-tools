# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from uuid import uuid4

from odoo import exceptions, fields
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestIrSequence(TransactionCase):
    """
    Tests for ir.sequence
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.Sequence = cls.env["ir.sequence"]
        cls.sequence = cls.Sequence.create(
            {
                "name": "Test sequence",
                "code": "test.custom.sequence",
                "prefix": "",
                "padding": 2,
                "number_next": 1,
                "number_increment": 1,
                "company_id": False,
            }
        )
        cls.test_code = str(uuid4())

        def _get_special_values(self, date=None, date_range=None):
            return {"test_code": cls.test_code}

        cls.Sequence._patch_method("_get_special_values", _get_special_values)

    def test_get_prefix_suffix1(self):
        """
        For this test, we use a prefix who mix custom variables and odoo variables
        to ensure both are compatible.
        :return:
        """
        self.sequence.write({"prefix": "%(year)s{test_code}"})
        prefix, _suffix = self.sequence._get_prefix_suffix()
        year = fields.Date.today().year
        expected_result = "{year}{code}".format(year=year, code=self.test_code)
        self.assertEqual(expected_result, prefix)

    def test_get_prefix_suffix2(self):
        """
        For this test, we use a prefix who use only Odoo variables,
        to ensure the standard is not broken.
        :return:
        """
        self.sequence.write({"prefix": "%(year)s"})
        prefix, _suffix = self.sequence._get_prefix_suffix()
        year = fields.Date.today().year
        expected_result = "{year}".format(year=year)
        self.assertEqual(expected_result, prefix)

    def test_get_prefix_suffix3(self):
        """
        For this test, we use a prefix who use only custom variables,
        to ensure it's working!
        :return:
        """
        self.sequence.write({"prefix": "{test_code}"})
        prefix, _suffix = self.sequence._get_prefix_suffix()
        expected_result = "{code}".format(code=self.test_code)
        self.assertEqual(expected_result, prefix)

    def test_get_prefix_suffix4(self):
        """
        For this test, we use an empty prefix to ensure it stills working!
        :return:
        """
        self.sequence.write({"prefix": ""})
        prefix, _suffix = self.sequence._get_prefix_suffix()
        expected_result = ""
        self.assertEqual(expected_result, prefix)

    def test_get_prefix_suffix5(self):
        """
        For this test, we use a prefix who mix custom variables, odoo variables
        and some letters to ensure both are compatible.
        :return:
        """
        self.sequence.write({"prefix": "E%(year)sd{test_code}AB"})
        prefix, _suffix = self.sequence._get_prefix_suffix()
        year = fields.Date.today().year
        expected_result = "E{year}d{code}AB".format(year=year, code=self.test_code)
        self.assertEqual(expected_result, prefix)

    @mute_logger("odoo.addons.sequence_custom_data.models.ir_sequence")
    def test_get_prefix_suffix6(self):
        """
        For this test, we use a code who is not defined.
        We ensure the exception is correctly triggered.
        :return:
        """
        self.sequence.write({"prefix": "{test_code_not_exist}"})
        with self.assertRaises(exceptions.UserError) as em:
            self.sequence._get_prefix_suffix()
        # Just to ensure it's the expected exception.
        expected_msg = "Please check prefix and suffix with available values"
        self.assertIn(expected_msg, em.exception.args[0])
        self.assertIn(self.sequence.code, em.exception.args[0])
