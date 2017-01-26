# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.

import mock

from odoo.tests import common


ADAPTER = ('odoo.addons.base_external_dbsource_sqlite.models'
           '.base_external_dbsource.sqlalchemy')


class TestBaseExternalDbsource(common.TransactionCase):

    def setUp(self):
        super(TestBaseExternalDbsource, self).setUp()
        self.dbsource = self.env.ref(
            'base_external_dbsource_sqlite.demo_sqlite',
        )

    def test_connection_close_sqlite(self):
        """ It should close the connection """
        connection = mock.MagicMock()
        res = self.dbsource.connection_close_sqlite(connection)
        self.assertEqual(res, connection.close())

    def test_connection_open_sqlite(self):
        """ It should call SQLAlchemy open """
        with mock.patch.object(
            self.dbsource, '_connection_open_sqlalchemy'
        ) as parent_method:
            self.dbsource.connection_open_sqlite()
            parent_method.assert_called_once_with()

    def test_excecute_sqlite(self):
        """ It should pass args to SQLAlchemy execute """
        expect = 'sqlquery', 'sqlparams', 'metadata'
        with mock.patch.object(
            self.dbsource, '_execute_sqlalchemy'
        ) as parent_method:
            self.dbsource.execute_sqlite(*expect)
            parent_method.assert_called_once_with(*expect)
