# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.exceptions import ValidationError


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
