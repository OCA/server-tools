# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger
from psycopg2 import IntegrityError


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

    def test_unlink(self):
        date_range = self.env['date.range']
        drt = self.env['date.range.type'].create(
            {'name': 'Fiscal year',
             'allow_overlap': False})
        date_range.create({
            'name': 'FS2016',
            'date_start': '2015-01-01',
            'date_end': '2016-12-31',
            'type_id': drt.id,
        })
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            drt.unlink()
