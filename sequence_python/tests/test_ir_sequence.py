# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestIrSequence(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Sequence = cls.env["ir.sequence"]
        cls.sequence = cls.Sequence.create(
            {
                "name": "Test sequence",
                "implementation": "standard",
                "code": "test.python.sequence",
                "prefix": "A",
                "padding": 2,
                "number_next": 1,
                "number_increment": 1,
                "company_id": False,
                "use_python_code": True,
                "python_code": "'B' + number_padded + 'C'",
            }
        )

    def test_non_python_sequence(self):
        """Verify if non-Python sequences still work"""
        self.sequence.number_next_actual = 1
        self.sequence.use_python_code = False
        next_number = self.sequence._next()
        self.assertEqual(next_number, "A01")

    def test_standard_sequence(self):
        self.sequence.number_next_actual = 1
        self.assertEqual(self.sequence.python_code_preview, "AB01C")
        next_number = self.sequence._next()
        self.assertEqual(next_number, "AB01C")
        next_number = self.sequence._next()
        self.assertEqual(next_number, "AB02C")

    def test_nogap_sequence(self):
        self.sequence.write(dict(implementation="no_gap"))
        next_number = self.sequence._next()
        self.assertEqual(next_number, "AB01C")
        next_number = self.sequence._next()
        self.assertEqual(next_number, "AB02C")

    def test_preview_with_wrong_python_syntax(self):
        # This will raise a Python TypeError exception
        self.sequence.python_code = "number_padded + 1"
        # It will not raise but put the Exception text in the preview field
        self.assertIn("TypeError", self.sequence.python_code_preview)
