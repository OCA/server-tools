# -*- coding: utf-8 -*-

from openerp.exceptions import Warning as UserError
from openerp.tests import common
import logging

class TestCreateDbsource(common.TransactionCase):
    """Test class for base_external_dbsource."""

    def test_create_dbsource(self):
        """Test source creation."""
        dbsource = self.env.ref('base_external_dbsource.demo_postgre')
        try:
            dbsource.connection_test()
        except UserError as e:
            logging.warning("Log = "+str(e))
            self.assertTrue(u'Everything seems properly set up!' in str(e))
