# -*- coding: utf-8 -*-
# © 2016  Vauxoo (<http://www.vauxoo.com/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os

from openerp.tests import common
from openerp.tools.convert import convert_file


class TestConvertFile(common.TransactionCase):
    """Test convert_file method patched
    """

    def setUp(self):
        super(TestConvertFile, self).setUp()
        self.module = os.path.basename(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        self.fdemo = 'demo/partner_category_demo.xml'
        self.fdata = 'data/partner_category_data.xml'
        self.fdata2 = 'data/partner_category_data2.xml'

    def tearDown(self):
        super(TestConvertFile, self).tearDown()
        self.registry['ir.model.data'].clear_caches()

    def test_10_demo_ref_from_data(self):
        """Test demo referenced from data
        """
        convert_file(self.cr, self.module, self.fdemo, None, kind='demo')
        convert_file(self.cr, self.module, self.fdata, None, kind='data')

    def test_20_demo_overwritten_from_data(self):
        """Test demo overwritten from data
        """
        convert_file(self.cr, self.module, self.fdemo, None, kind='demo')
        convert_file(self.cr, self.module, self.fdata2, None, kind='data')
