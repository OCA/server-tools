# Copyright 2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSequenceStandardDefault(TransactionCase):

    def setUp(self):

        super(TestSequenceStandardDefault, self).setUp()
        self.wizard = self.env['sequence.standard.default'].create({})
        self.seq_nogap = self.env['ir.sequence'].create({
            'name': 'NoGap Sequence',
            'implementation': 'no_gap',
            'use_date_range': False,
            'number_next_actual': 100,
        })
        self.seq_nogap_range = self.env['ir.sequence'].create({
            'name': 'NoGap Sequence with Date Range',
            'implementation': 'no_gap',
            'use_date_range': True,
        })
        self.date_range = self.env['ir.sequence.date_range'].create({
            'sequence_id': self.seq_nogap_range.id,
            'date_from': '2019-01-01',
            'date_to': '2019-12-31',
            'number_next_actual': 200,
        })
        self.seq_standard = self.env['ir.sequence'].create({
            'name': 'Standard Sequence',
            'implementation': 'standard',
            'number_next_actual': 300,
        })

    def test01_nogap_to_std(self):
        self.wizard.execute()

        self.assertEqual(self.seq_nogap.implementation, 'standard')
        self.assertEqual(self.seq_nogap.number_next_actual, 100)

        self.assertEqual(self.seq_nogap_range.implementation, 'standard')
        self.assertEqual(self.date_range.number_next_actual, 200)

        self.assertEqual(self.seq_standard.implementation, 'standard')
        self.assertEqual(self.seq_standard.number_next_actual, 300)
