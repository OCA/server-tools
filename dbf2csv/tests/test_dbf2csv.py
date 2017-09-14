# -*- coding: utf-8 -*-
# Copyright 2017 INGETIVE (<https://ingetive.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestConversion(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestConversion, self).setUp(*args, **kwargs)
        # Get demo conversions
        self.conversion_test = self.env.ref('dbf2csv.demo_conversion_1')

    def test__conversions(self):
        "Only check that the conversion process finished satifactory, name for csv file was created"
        self.conversion_test.process_file()
        filename_csv_test = self.conversion_test.filename_csv
        self.assertEqual(filename_csv_test, 'demo.csv', 'Wrong number of conversions')
