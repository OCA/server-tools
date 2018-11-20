# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)nses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from dateutil.rrule import MONTHLY


class DateRangeGeneratorTest(TransactionCase):

    def setUp(self):
        super(DateRangeGeneratorTest, self).setUp()
        self.generator = self.env['date.range.generator']
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

    def test_generate(self):
        generator = self.generator.create({
            'date_start': '1943-01-01',
            'name_prefix': '1943-',
            'type_id': self.type.id,
            'duration_count': 3,
            'unit_of_time': MONTHLY,
            'count': 4})
        generator.action_apply()
        ranges = self.env['date.range'].search(
            [('type_id', '=', self.type.id)])
        self.assertEquals(len(ranges), 4)
        range4 = ranges[3]
        self.assertEqual(range4.date_start, '1943-10-01')
        self.assertEqual(range4.date_end, '1943-12-31')
        self.assertEqual(range4.type_id, self.type)

    def test_generator_multicompany_1(self):
        generator = self.generator.new({
            'date_start': '1943-01-01',
            'name_prefix': '1943-',
            'type_id': self.typeB.id,
            'duration_count': 3,
            'unit_of_time': MONTHLY,
            'count': 4,
            'company_id': self.company.id,
        })
        generator._cache.update(generator._convert_to_cache(
            {'company_id': self.company_2.id}, update=True))
        generator._onchange_company_id()
        self.assertFalse(generator.type_id)

    def test_generator_multicompany_2(self):
        with self.assertRaises(ValidationError):
            self.generator.create({
                'date_start': '1943-01-01',
                'name_prefix': '1943-',
                'type_id': self.typeB.id,
                'duration_count': 3,
                'unit_of_time': MONTHLY,
                'count': 4,
                'company_id': self.company_2.id,
            })

    def test_generator_partner_id_domain(self):
        """Check here domain returned for partner_id
        in both date.range and date.range.generator"""
        date_range = self.env['date.range']
        generator = self.env['date.range.generator']
        date_type = self.env['date.range.type']
        month_type = date_type.create({
            'name': 'month type'
        })
        day_type = date_type.create({
            'name': 'day type',
            'parent_type_id': month_type.id,
        })
        month_range = date_range.create({
            'name': 'month range',
            'type_id': month_type.id,
            'date_start': '01-01-2050',
            'date_end': '02-01-2050',
        })
        # now trigger onchange in generator,
        # which would also trigger onchange in date_range
        values = {
            'date_start': month_range.date_start,
            'type_id': day_type.id,
        }
        on_change = generator._onchange_spec()
        domain = generator.onchange(
            values,
            ['type_id', 'date_start'],
            on_change,
        )
        # check that with this search domain,
        # only the month_range record is returned.
        self.assertEqual(
            date_range.search(domain['domain']['parent_id']),
            month_range,
        )
