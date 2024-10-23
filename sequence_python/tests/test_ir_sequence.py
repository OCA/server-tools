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
