# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.

import mock

from odoo.tests import common


ADAPTER = ('odoo.addons.base_external_dbsource_firebird.models'
           '.base_external_dbsource.fdb')


class TestBaseExternalDbsource(common.TransactionCase):

    def setUp(self):
        super(TestBaseExternalDbsource, self).setUp()
        self.dbsource = self.env.ref(
            'base_external_dbsource_firebird.demo_firebird',
        )

    def test_connection_close_fdb(self):
        """ It should close the connection """
        connection = mock.MagicMock()
        res = self.dbsource.connection_close_fdb(connection)
        self.assertEqual(res, connection.close())

    @mock.patch(ADAPTER)
    def test_connection_open_fdb(self, fdb):
        """ It should open the connection with the split conn string """
        self.dbsource.conn_string = 'User=User;'
        self.dbsource.connection_open_fdb()
        fdb.connect.assert_called_once_with(**{
            'user': 'User',
            'password': 'password',
        })

    @mock.patch(ADAPTER)
    def test_connection_open_fdb_return(self, fdb):
        """ It should return the newly opened connection """
        res = self.dbsource.connection_open_fdb()
        self.assertEqual(res, fdb.connect())
