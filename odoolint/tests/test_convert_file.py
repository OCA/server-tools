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
        self.current_module = os.path.basename(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        self.fdemo = 'demo/partner_category_demo.xml'
        self.fdata = 'data/partner_category_data.xml'

    def test_demo_ref_from_data(self):
        """Test demo referenced from data
        """
        convert_file(self.cr, self.current_module, self.fdemo,
                     None, kind='demo')
        convert_file(self.cr, self.current_module, self.fdata,
                     None, kind='data')
