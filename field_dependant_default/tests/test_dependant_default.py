# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestDependantDefault(common.TransactionCase):

    def test_dependant_default(self):
        record = self.env['dependant_default.test'].create({
            'value': 'testing',
        })

        self.assertEqual(record.partner_id, self.env.user.partner_id)
        self.assertEqual(record.dependant_value, 'TESTING')
        self.assertEqual(record.dependant_integer, 7)

    def test_dependant_default_with_value(self):
        record = self.env['dependant_default.test'].create({
            'value': 'testing',
            'dependant_integer': 2,
            'partner_id': (4, self.browse_ref('base.main_partner').id),
        })
        self.assertNotEqual(record.partner_id, self.env.user.partner_id)
        self.assertEqual(record.dependant_value, 'TESTING')
        self.assertEqual(record.dependant_integer, 2)
