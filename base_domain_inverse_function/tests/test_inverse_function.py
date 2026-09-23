# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.osv.expression import AND, OR
from odoo.tests import TransactionCase

from ..inverse_expression import inverse_AND, inverse_OR


class TestInverseFunctions(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.basic_domain_and = ["&", "&", ("a", "=", 1), ("b", "=", 2), ("c", "=", 3)]
        cls.basic_domain_or = ["|", "|", ("a", "=", 1), ("b", "=", 2), ("c", "=", 3)]
        cls.complex_domain_and_and_or = (
            ["&"] + cls.basic_domain_and + cls.basic_domain_or
        )
        cls.complex_domain_or_or_and = (
            ["|"] + cls.basic_domain_or + cls.basic_domain_and
        )
        cls.complex_domain_and_or_or = ["&"] + cls.basic_domain_or + cls.basic_domain_or
        cls.complex_domain_or_and_and = (
            ["|"] + cls.basic_domain_and + cls.basic_domain_and
        )

    def test_neutral_basic_and(self):
        result = AND(inverse_AND(self.basic_domain_and))
        self.assertEqual(result, self.basic_domain_and)

    def test_neutral_basic_or(self):
        result = OR(inverse_OR(self.basic_domain_or))
        self.assertEqual(result, self.basic_domain_or)

    def test_neutral_complex_and_and_or(self):
        result = AND(inverse_AND(self.complex_domain_and_and_or))
        self.assertEqual(result, self.complex_domain_and_and_or)

    def test_neutral_complex_or_or_and(self):
        result = OR(inverse_OR(self.complex_domain_or_or_and))
        self.assertEqual(result, self.complex_domain_or_or_and)

    def test_neutral_complex_and_or_or(self):
        result = AND(inverse_AND(self.complex_domain_and_or_or))
        self.assertEqual(result, self.complex_domain_and_or_or)

    def test_neutral_complex_or_and_and(self):
        result = OR(inverse_OR(self.complex_domain_or_and_and))
        self.assertEqual(result, self.complex_domain_or_and_and)

    def test_inverse_basic_and(self):
        result = [
            [("a", "=", 1)],
            [("b", "=", 2)],
            [("c", "=", 3)],
        ]
        self.assertEqual(inverse_AND(self.basic_domain_and), result)

    def test_inverse_basic_or(self):
        result = [
            [("a", "=", 1)],
            [("b", "=", 2)],
            [("c", "=", 3)],
        ]
        self.assertEqual(inverse_OR(self.basic_domain_or), result)

    def test_inverse_complex_and_and_or(self):
        result = [
            [("a", "=", 1)],
            [("b", "=", 2)],
            [("c", "=", 3)],
            ["|", "|", ("a", "=", 1), ("b", "=", 2), ("c", "=", 3)],
        ]
        self.assertEqual(inverse_AND(self.complex_domain_and_and_or), result)

    def test_inverse_complex_or_or_and(self):
        result = [
            [("a", "=", 1)],
            [("b", "=", 2)],
            [("c", "=", 3)],
            ["&", "&", ("a", "=", 1), ("b", "=", 2), ("c", "=", 3)],
        ]
        self.assertEqual(inverse_OR(self.complex_domain_or_or_and), result)

    def test_inverse_complex_and_or_or(self):
        result = [
            ["|", "|", ("a", "=", 1), ("b", "=", 2), ("c", "=", 3)],
            ["|", "|", ("a", "=", 1), ("b", "=", 2), ("c", "=", 3)],
        ]
        self.assertEqual(inverse_AND(self.complex_domain_and_or_or), result)

    def test_inverse_complex_or_and_and(self):
        result = [
            ["&", "&", ("a", "=", 1), ("b", "=", 2), ("c", "=", 3)],
            ["&", "&", ("a", "=", 1), ("b", "=", 2), ("c", "=", 3)],
        ]
        self.assertEqual(inverse_OR(self.complex_domain_or_and_and), result)
