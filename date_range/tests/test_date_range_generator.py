# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from dateutil.rrule import MONTHLY


class DateRangeGeneratorTest(TransactionCase):

    def setUp(self):
        super(DateRangeGeneratorTest, self).setUp()
        self.type = self.env['date.range.type'].create(
            {'name': 'Fiscal year',
             'company_id': False,
             'allow_overlap': False})

    def test_generate(self):
        generator = self.env['date.range.generator']
        generator = generator.create({
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

