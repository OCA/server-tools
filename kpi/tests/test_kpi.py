# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestKPI(TransactionCase):

    def setUp(self):
        super(TestKPI, self).setUp()

    def test_invalid_threshold_range(self):
        range1 = self.env['kpi.threshold.range'].create({
            'name': 'Range1',
            'min_type': 'static',
            'max_type': 'static',
            'min_fixed_value': 3,
            'max_fixed_value': 1,
        })
        range2 = self.env['kpi.threshold.range'].create({
            'name': 'Range2',
            'min_type': 'static',
            'max_type': 'static',
            'min_fixed_value': 4,
            'max_fixed_value': 10,
        })
        self.assertFalse(range1.valid)
        self.assertTrue(range2.valid)

    def test_invalid_threshold(self):
        range1 = self.env['kpi.threshold.range'].create({
            'name': 'Range1',
            'min_type': 'static',
            'max_type': 'static',
            'min_fixed_value': 1,
            'max_fixed_value': 4,
        })
        range2 = self.env['kpi.threshold.range'].create({
            'name': 'Range2',
            'min_type': 'static',
            'max_type': 'static',
            'min_fixed_value': 4,
            'max_fixed_value': 10,
        })
        range3 = self.env['kpi.threshold.range'].create({
            'name': 'Range3',
            'min_type': 'static',
            'max_type': 'static',
            'min_fixed_value': 1,
            'max_fixed_value': 3,
        })
        range_invalid = self.env['kpi.threshold.range'].create({
            'name': 'RangeInvalid',
            'min_type': 'static',
            'max_type': 'static',
            'min_fixed_value': 3,
            'max_fixed_value': 1,
        })

        threshold1 = self.env['kpi.threshold'].create({
            'name': 'Threshold1',
            'range_ids': [(6, 0, [range1.id, range2.id])],
        })

        threshold2 = self.env['kpi.threshold'].create({
            'name': 'Threshold1',
            'range_ids': [(6, 0, [range3.id, range2.id])],
        })

        threshold3 = self.env['kpi.threshold'].create({
            'name': 'Threshold1',
            'range_ids': [(6, 0, [range_invalid.id, range2.id])],
        })

        self.assertFalse(threshold1.valid)
        self.assertTrue(threshold2.valid)
        self.assertFalse(threshold3.valid)

    def test_invalid_threshold_range_exception(self):
        range_error = self.env['kpi.threshold.range'].create({
            'name': 'RangeError',
            'min_type': 'python',
            'min_code': '<Not a valid python expression>',
            'max_type': 'static',
            'max_fixed_value': 1,
        })
        self.assertFalse(range_error.valid)
