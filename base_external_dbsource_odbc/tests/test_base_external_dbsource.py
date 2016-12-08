# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.

import mock

from odoo.tests import common


ADAPTER = ('odoo.addons.base_external_dbsource_odbc.models'
           '.base_external_dbsource.pyodbc')


class TestBaseExternalDbsource(common.TransactionCase):

    def setUp(self):
        super(TestBaseExternalDbsource, self).setUp()
        self.dbsource = self.env.ref(
            'base_external_dbsource_odbc.demo_odbc',
        )

    def test_connection_close_pyodbc(self):
        """ It should close the connection """
        connection = mock.MagicMock()
        res = self.dbsource.connection_close_pyodbc(connection)
        self.assertEqual(res, connection.close())

    @mock.patch(ADAPTER)
    def test_connection_open_pyodbc(self, pyodbc):
        """ It should open the connection with the full conn string """
        self.dbsource.connection_open_pyodbc()
        pyodbc.connect.assert_called_once_with(
            self.dbsource.conn_string_full,
        )

    @mock.patch(ADAPTER)
    def test_connection_open_pyodbc_return(self, pyodbc):
        """ It should return the newly opened connection """
        res = self.dbsource.connection_open_pyodbc()
        self.assertEqual(res, pyodbc.connect())

    def test_execute_pyodbc(self):
        """ It should call the generic execute method w/ proper args """
        expect = 'sqlquery', 'sqlparams', 'metadata'
        with mock.patch.object(self.dbsource, '_execute_generic') as execute:
            self.dbsource.execute_pyodbc(*expect)
            execute.assert_called_once_with(*expect)
