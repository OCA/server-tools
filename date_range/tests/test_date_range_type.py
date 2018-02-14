# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import TransactionCase


class DateRangeTypeTest(TransactionCase):

    def test_default_company(self):
        drt = self.env['date.range.type'].create(
            {'name': 'Fiscal year',
             'allow_overlap': False})
        self.assertTrue(drt.company_id)
        # you can specify company_id to False
        drt = self.env['date.range.type'].create(
            {'name': 'Fiscal year',
             'company_id': False,
             'allow_overlap': False})
        self.assertFalse(drt.company_id)
