# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class DateRangeTest(TransactionCase):

    def setUp(self):
        super(DateRangeTest, self).setUp()
        self.date_range = self.env['date.range']
        self.type = self.env['date.range.type'].create(
            {'name': 'Fiscal year',
             'company_id': False,
             'allow_overlap': False})

        self.company = self.env['res.company'].create({
            'name': 'Test company',
        })
        self.company_2 = self.env['res.company'].create({
            'name': 'Test company 2',
            'parent_id': self.company.id,
        })
        self.typeB = self.env['date.range.type'].create(
            {'name': 'Fiscal year B',
             'company_id': self.company.id,
             'allow_overlap': False})

    def test_default_company(self):
        dr = self.date_range.create({
            'name': 'FS2016',
            'date_start': '2015-01-01',
            'date_end': '2016-12-31',
            'type_id': self.type.id,
        })
        self.assertTrue(dr.company_id)
        # you can specify company_id to False
        dr = self.date_range.create({
            'name': 'FS2016_NO_COMPANY',
            'date_start': '2015-01-01',
            'date_end': '2016-12-31',
            'type_id': self.type.id,
            'company_id': False
        })
        self.assertFalse(dr.company_id)

    def test_empty_company(self):
        dr = self.date_range.create({
            'name': 'FS2016',
            'date_start': '2015-01-01',
            'date_end': '2016-12-31',
            'type_id': self.type.id,
            'company_id': None,
        })
        self.assertEqual(dr.name, 'FS2016')

    def test_invalid(self):
        with self.assertRaises(ValidationError) as cm:
            self.date_range.create({
                'name': 'FS2016',
                'date_end': '2015-01-01',
                'date_start': '2016-12-31',
                'type_id': self.type.id,
            })
        self.assertEqual(
            cm.exception.name,
            'FS2016 is not a valid range (2016-12-31 > 2015-01-01)')

    def test_overlap(self):
        self.date_range.create({
            'name': 'FS2015',
            'date_start': '2015-01-01',
            'date_end': '2015-12-31',
            'type_id': self.type.id,
        })
        with self.assertRaises(ValidationError) as cm, self.env.cr.savepoint():
            self.date_range.create({
                'name': 'FS2016',
                'date_start': '2015-01-01',
                'date_end': '2016-12-31',
                'type_id': self.type.id,
            })
        self.assertEqual(cm.exception.name, 'FS2016 overlaps FS2015')
        # check it's possible to overlap if it's allowed by the date range type
        self.type.allow_overlap = True
        dr = self.date_range.create({
            'name': 'FS2016',
            'date_start': '2015-01-01',
            'date_end': '2016-12-31',
            'type_id': self.type.id,
        })
        self.assertEquals(dr.name, 'FS2016')

    def test_domain(self):
        dr = self.date_range.create({
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

    def test_date_range_multicompany_1(self):
        dr = self.date_range.new({
            'name': 'FS2016',
            'date_start': '2015-01-01',
            'date_end': '2016-12-31',
            'type_id': self.typeB.id,
            'company_id': self.company.id,
        })
        dr._cache.update(dr._convert_to_cache(
            {'company_id': self.company_2.id}, update=True))
        dr._onchange_company_id()
        self.assertFalse(dr.type_id)

    def test_date_range_multicompany_2(self):
        with self.assertRaises(ValidationError):
            self.date_range.create({
                'name': 'FS2016',
                'date_start': '2015-01-01',
                'date_end': '2016-12-31',
                'type_id': self.typeB.id,
                'company_id': self.company_2.id,
            })

    def test_parent_id(self):
        date_range_type = self.env['date.range.type']
        parent = self.date_range.create({
            'name': 'FS2018',
            'date_start': '2018-01-01',
            'date_end': '2018-12-31',
            'type_id': self.type.id,
        })
        type_block = date_range_type.create({
            'name': 'FS2018-type_block',
            'company_id': False,
            'allow_overlap': False,
        })
        # Check here all three validation errors thrown
        # when child range is not a subrange of parent
        with self.assertRaises(ValidationError) as cm, self.env.cr.savepoint():
            self.date_range.create({
                'name': 'FS2018-period1',
                'date_start': '2018-06-06',
                'date_end': '2019-01-02',
                'type_id': type_block.id,
                'parent_id': parent.id,
            })
        self.assertEqual(
            cm.exception.name,
            'FS2018-period1 not a subrange of FS2018: '
            'End dates are not compatible (2019-01-02 > 2018-12-31)'
        )
        with self.assertRaises(ValidationError) as cm, self.env.cr.savepoint():
            self.date_range.create({
                'name': 'FS2018-period1',
                'date_start': '2017-06-06',
                'date_end': '2018-01-02',
                'type_id': type_block.id,
                'parent_id': parent.id,
            })
        self.assertEqual(
            cm.exception.name,
            'FS2018-period1 not a subrange of FS2018: '
            'Start dates are not compatible (2017-06-06 < 2018-01-01)'
        )
        with self.assertRaises(ValidationError) as cm, self.env.cr.savepoint():
            self.date_range.create({
                'name': 'FS2018-period1',
                'date_start': '2017-06-06',
                'date_end': '2019-01-02',
                'type_id': type_block.id,
                'parent_id': parent.id,
            })
        self.assertEqual(
            cm.exception.name,
            'FS2018-period1 not a subrange of FS2018: '
            'FS2018-period1 range not in 2018-01-01 - 2018-12-31'
        )
        self.date_range.create({
            'name': 'FS2018-period1',
            'date_start': '2018-01-01',
            'date_end': '2018-04-30',
            'type_id': type_block.id,
            'parent_id': parent.id,
        })
        # Check here that a validation error is thrown
        # when child periods overlap
        with self.assertRaises(ValidationError) as cm, self.env.cr.savepoint():
            self.date_range.create({
                'name': 'FS2018-period2',
                'date_start': '2018-02-01',
                'date_end': '2018-03-15',
                'type_id': type_block.id,
                'parent_id': parent.id,
            })
        self.assertEqual(
            cm.exception.name,
            'FS2018-period2 overlaps FS2018-period1'
        )

    def test_parent_type_id(self):
        """Check domain and constraint between parent and child types"""
        date_range_type = self.env['date.range.type']
        # First create a parent type
        parent_type = date_range_type.create({
            'name': 'FS2018_parent_type',
            'parent_type_id': False,
        })
        # catch here the validation error when assigning
        # a date_range_type parent, to another parent(self included)
        with self.assertRaises(ValidationError)as cm, self.env.cr.savepoint():
            parent_type.write({
                'parent_type_id': parent_type.id,
            })
        self.assertEqual(
            cm.exception.name,
            'A type parent  can not have a parent:'
            ' FS2018_parent_type can not have FS2018_parent_type as parent'
        )
        # Then, add a child type
        child_type = date_range_type.create({
            'name': 'FS2018_child_type',
            'parent_type_id': parent_type.id,
        })
        # Now create a parent range
        parent_range = self.date_range.create({
            'name': 'FS2018',
            'date_start': '2018-01-01',
            'date_end': '2018-12-31',
            'type_id': parent_type.id,
        })
        # and two child ranges
        child_range1 = self.date_range.create({
            'name': 'FS2018-child1',
            'date_start': '2018-01-01',
            'date_end': '2018-04-30',
            'type_id': child_type.id,
            'parent_id': parent_range.id,
        })
        child_range2 = self.date_range.create({
            'name': 'FS2018-child2',
            'date_start': '2018-05-01',
            'date_end': '2018-06-30',
            'type_id': child_type.id,
            'parent_id': parent_range.id,
        })
        # and check how parent_type_id behaves
        self.assertEqual(parent_type, child_range1.parent_type_id)
        self.assertEqual(
            child_range1.parent_type_id,
            child_range2.parent_type_id
        )
        # Ensure here that parent and children are of different type
        self.assertNotEqual(
            parent_range.type_id,
            child_range1.type_id
        )
        self.assertEqual(
            parent_range.type_id,
            child_range2.parent_id.type_id
        )
