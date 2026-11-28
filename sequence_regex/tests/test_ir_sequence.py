# Copyright 2026 manaTec GmbH (<https://manatec.de>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSequence(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_static_prefix(self):
        sequence = self.env["ir.sequence"].create(
            {"name": "Static Prefix Sequence", "prefix": "PRE/", "padding": 4}
        )
        name = sequence._next_do()
        regex = sequence._get_sequence_regex_pattern()
        fits = sequence.name_fits_sequence(name)
        self.assertEqual(regex, r"PRE/\d{4,}")
        self.assertRegex(name, regex)
        self.assertTrue(fits)

    def test_dynamic_prefix(self):
        sequence = self.env["ir.sequence"].create(
            {"name": "Dynamic Prefix Sequence", "prefix": "PRE/%(year)s/", "padding": 4}
        )
        name = sequence._next_do()
        regex = sequence._get_sequence_regex_pattern()
        fits = sequence.name_fits_sequence(name)
        self.assertEqual(regex, r"PRE/(19|20|21)\d{2}/\d{4,}")
        self.assertRegex(name, regex)
        self.assertTrue(fits)

    def test_mismatch(self):
        sequence_1 = self.env["ir.sequence"].create(
            {"name": "Static Prefix Sequence", "prefix": "PRE/", "padding": 4}
        )
        sequence_2 = self.env["ir.sequence"].create(
            {"name": "Dynamic Prefix Sequence", "prefix": "PRE/%(year)s/", "padding": 4}
        )
        name = sequence_2._next_do()
        fits = sequence_1.name_fits_sequence(name)
        self.assertFalse(fits)
