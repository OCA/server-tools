# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase
from odoo import fields


class TestIrSequenceDateRange(TransactionCase):
    """
    Tests for ir.sequence.date_range
    """

    def setUp(self):
        super(TestIrSequenceDateRange, self).setUp()
        self.sequence = self.env.ref(
            "sequence_date_range.ir_sequence_demo")

    def _get_current_date_range(self, sequence=False):
        """
        Get the sequence date range related to the current date
        :param sequence: ir.sequence recordset
        :return: ir.sequence.date_range recordset
        """
        sequence = sequence or self.sequence
        today = fields.Date.today()
        if self.env.context.get('ir_sequence_date'):
            today = self.env.context.get('ir_sequence_date')
        seq_date = self.env['ir.sequence.date_range'].search([
            ('sequence_id', '=', sequence.id),
            ('date_from', '<=', today),
            ('date_to', '>=', today),
        ], limit=1)
        return seq_date

    def test_using_date_range1(self):
        """
        Test the date range sequence.
        Check if the date (used into the generated sequence) is the one set
        into the date_to field (instead of date_from)
        :return:
        """
        self.assertEquals(self.sequence.date_range_field, 'date_to')
        current_date_range = self._get_current_date_range()
        date_to = fields.Date.from_string(current_date_range.date_to)
        value = self.sequence._next()
        expected_str = date_to.strftime("%Y-%m-%d")
        self.assertIn(expected_str, value)
        return

    def test_using_date_range2(self):
        """
        Test the date range sequence.
        Check if the date (used into the generated sequence) is the one set
        into the date_from field
        :return:
        """
        self.sequence.write({
            'date_range_field': 'date_from',
        })
        self.assertEquals(self.sequence.date_range_field, 'date_from')
        current_date_range = self._get_current_date_range()
        date_from = fields.Date.from_string(current_date_range.date_from)
        value = self.sequence._next()
        expected_str = date_from.strftime("%Y-%m-%d")
        self.assertIn(expected_str, value)
        return
