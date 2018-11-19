# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger
from psycopg2 import IntegrityError
from odoo.exceptions import ValidationError


class DateRangeTypeTest(TransactionCase):

    def setUp(self):
        super(DateRangeTypeTest, self).setUp()
        self.type = self.env['date.range.type']
        self.company = self.env['res.company'].create({
            'name': 'Test company',
        })
        self.company_2 = self.env['res.company'].create({
            'name': 'Test company 2',
            'parent_id': self.company.id,
        })

    def test_default_company(self):
        drt = self.type.create(
            {'name': 'Fiscal year',
             'allow_overlap': False})
        self.assertTrue(drt.company_id)
        # you can specify company_id to False
        drt = self.type.create(
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

    def test_type_multicompany(self):
        drt = self.type.create(
            {'name': 'Fiscal year',
             'company_id': False,
             'allow_overlap': False})
        self.env['date.range'].create({
            'name': 'FS2016',
            'date_start': '2015-01-01',
            'date_end': '2016-12-31',
            'type_id': drt.id,
            'company_id': self.company.id,
        })
        with self.assertRaises(ValidationError):
            drt.company_id = self.company_2
