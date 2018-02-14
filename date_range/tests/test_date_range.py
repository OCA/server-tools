# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class DateRangeTest(TransactionCase):

    def setUp(self):
        super(DateRangeTest, self).setUp()
        self.type = self.env['date.range.type'].create(
            {'name': 'Fiscal year',
             'company_id': False,
             'allow_overlap': False})

    def test_default_company(self):
        date_range = self.env['date.range']
        dt = date_range.create({
            'name': 'FS2016',
            'date_start': '2015-01-01',
            'date_end': '2016-12-31',
            'type_id': self.type.id,
        })
        self.assertTrue(dt.company_id)
        # you can specify company_id to False
        dt = date_range.create({
            'name': 'FS2016_NO_COMPANY',
            'date_start': '2015-01-01',
            'date_end': '2016-12-31',
            'type_id': self.type.id,
            'company_id': False
        })
        self.assertFalse(dt.company_id)

    def test_empty_company(self):
        date_range = self.env['date.range']
        dt = date_range.create({
            'name': 'FS2016',
            'date_start': '2015-01-01',
            'date_end': '2016-12-31',
            'type_id': self.type.id,
            'company_id': None,
        })
        self.assertEqual(dt.name, 'FS2016')

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
            'FS2016 is not a valid range (2016-12-31 > 2015-01-01)')

    def test_overlap(self):
        date_range = self.env['date.range']
        date_range.create({
            'name': 'FS2015',
            'date_start': '2015-01-01',
            'date_end': '2015-12-31',
            'type_id': self.type.id,
        })
        with self.assertRaises(ValidationError) as cm, self.env.cr.savepoint():
            date_range.create({
                'name': 'FS2016',
                'date_start': '2015-01-01',
                'date_end': '2016-12-31',
                'type_id': self.type.id,
            })
        self.assertEqual(cm.exception.name, 'FS2016 overlaps FS2015')
        # check it's possible to overlap if it's allowed by the date range type
        self.type.allow_overlap = True
        dr = date_range.create({
            'name': 'FS2016',
            'date_start': '2015-01-01',
            'date_end': '2016-12-31',
            'type_id': self.type.id,
        })
        self.assertEquals(dr.name, 'FS2016')

    def test_domain(self):
        date_range = self.env['date.range']
        dr = date_range.create({
            'name': 'FS2015',
            'date_start': '2015-01-01',
            'date_end': '2015-12-31',
            'type_id': self.type.id,
        })
        domain = dr.get_domain('my_field')
        # By default the domain include limits
        self.assertEquals(
            domain,
            [('my_field', '>=', '2015-01-01'),
             ('my_field', '<=', '2015-12-31')])
