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

    def test_standard_sequence(self):
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

    def test_python_code_returns_int(self):
        # Create a separate sequence for this test to avoid interference
        seq = self.Sequence.create(
            {
                "name": "Test sequence for int",
                "implementation": "standard",
                "code": "test.python.sequence.int",
                "prefix": "A",
                "padding": 0,  # No padding for this test
                "number_next": 1,
                "number_increment": 1,
                "company_id": False,
                "use_python_code": True,
                "python_code": "number",  # This returns an integer
            }
        )
        self.assertEqual(seq.python_code_preview, "A1")
        next_number = seq._next()
        self.assertEqual(next_number, "A1")

    def test_python_code_with_error(self):
        self.sequence.write({"python_code": "1 / 0"})
        self.assertIn("division by zero", self.sequence.python_code_preview)
