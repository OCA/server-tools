# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.exceptions import ValidationError


class DateRangeTest(TransactionCase):

    def setUp(self):
        super(DateRangeTest, self).setUp()
        self.type = self.env['date.range.type'].create(
            {'name': 'Fiscal year',
             'company_id': False,
             'allow_overlap': False})

    def test_invalid(self):
        date_range = self.env['date.range']
        with self.assertRaises(ValidationError) as cm:
            date_range.create({
                'name': 'FS2016',
                'date_end': '2015-01-01',
                'date_start': '2016-12-31',
                'type_id': self.type.id,
            })
        self.assertEqual(
            cm.exception.name,
            'FS2016 is not a valid range (2016-12-31 >= 2015-01-01)')

    def test_overlap(self):
        date_range = self.env['date.range']
        dr1 = date_range.create({
            'name': 'FS2015',
            'date_start': '2015-01-01',
            'date_end': '2015-12-31',
            'type_id': self.type.id,
        })
        with self.assertRaises(ValidationError) as cm:
            date_range.create({
                'name': 'FS2016',
                'date_start': '2015-01-01',
                'date_end': '2016-12-31',
                'type_id': self.type.id,
            })
        self.assertEqual(cm.exception.name, 'FS2016 overlaps FS2015')
