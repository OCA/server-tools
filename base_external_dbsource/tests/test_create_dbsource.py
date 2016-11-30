# -*- coding: utf-8 -*-

from odoo.exceptions import Warning as UserError
from odoo.tests import common
import logging


class TestCreateDbsource(common.TransactionCase):
    """Test class for base_external_dbsource."""

    def test_create_dbsource(self):
        """source creation should succeed."""
        dbsource = self.env.ref('base_external_dbsource.demo_postgre')
        try:
            dbsource.connection_test()
        except UserError as e:
            logging.warning("Log = " + str(e))
            self.assertTrue(u'Everything seems properly set up!' in str(e))

    def test_create_dbsource_failed(self):
        """source creation without connection string should failed."""
        dbsource = self.env.ref('base_external_dbsource.demo_postgre')

        # Connection without connection_string
        dbsource.conn_string = ""
        try:
            dbsource.connection_test()
        except UserError as e:
            logging.warning("Log = " + str(e))
            self.assertTrue(u'Here is what we got instead:' in str(e))

    def test_create_dbsource_without_connector_failed(self):
        """source creation with other connector should failed."""
        dbsource = self.env.ref('base_external_dbsource.demo_postgre')

        # Connection to mysql
        try:
            dbsource.connector = "mysql"
            dbsource.connection_test()
        except ValueError as e:
            logging.warning("Log = " + str(e))
            self.assertTrue(u'Wrong value for' in str(e))

        # Connection to mysql
        try:
            dbsource.connector = "pyodbc"
            dbsource.connection_test()
        except ValueError as e:
            logging.warning("Log = " + str(e))
            self.assertTrue(u'Wrong value for' in str(e))

        # Connection to oracle
        try:
            dbsource.connector = "cx_Oracle"
            dbsource.connection_test()
        except ValueError as e:
            logging.warning("Log = " + str(e))
            self.assertTrue(u'Wrong value for' in str(e))

        # Connection to firebird
        try:
            dbsource.connector = "fdb"
            dbsource.connection_test()
        except Exception as e:
            logging.warning("Log = " + str(e))
            self.assertTrue(u'Wrong value for' in str(e))
