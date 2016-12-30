# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.

import mock

from openerp.tests import common

from ..exceptions import ConnectionFailedError, ConnectionSuccessError


class TestBaseExternalDbsource(common.TransactionCase):

    def setUp(self):
        super(TestBaseExternalDbsource, self).setUp()
        self.dbsource = self.env.ref('base_external_dbsource.demo_postgre')

    def _test_adapter_method(
        self, method_name, side_effect=None, return_value=None,
        create=False, args=None, kwargs=None,
    ):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        adapter = '%s_postgresql' % method_name
        with mock.patch.object(self.dbsource,
                               adapter, create=create) as adapter:
            if side_effect is not None:
                adapter.side_effect = side_effect
            elif return_value is not None:
                adapter.return_value = return_value
            res = getattr(self.dbsource, method_name)(*args, **kwargs)
            return res, adapter

    def test_conn_string_full(self):
        """ It should add password if string interpolation not detected """
        self.dbsource.conn_string = 'User=Derp;'
        self.dbsource.password = 'password'
        expect = self.dbsource.conn_string + 'PWD=%s;' % self.dbsource.password
        self.assertEqual(
            self.dbsource.conn_string_full, expect,
        )

    # Interface

    def test_connection_success(self):
        """ It should raise for successful connection """
        with self.assertRaises(ConnectionSuccessError):
            self.dbsource.connection_test()

    def test_connection_fail(self):
        """ It should raise for failed/invalid connection """
        with mock.patch.object(self.dbsource, 'connection_open') as conn:
            conn.side_effect = Exception
            with self.assertRaises(ConnectionFailedError):
                self.dbsource.connection_test()

    def test_connection_open_calls_close(self):
        """ It should close connection after context ends """
        with mock.patch.object(
            self.dbsource, 'connection_close',
        ) as close:
            with self.dbsource.connection_open():
                pass
            close.assert_called_once()

    def test_connection_close(self):
        """ It should call adapter's close method """
        args = [mock.MagicMock()]
        res, adapter = self._test_adapter_method(
            'connection_close', args=args,
        )
        adapter.assert_called_once_with(args[0])

    def test_execute_asserts_query_arg(self):
        """ It should raise a TypeError if query and sqlquery not in args """
        with self.assertRaises(TypeError):
            self.dbsource.execute()

    def test_execute_calls_adapter(self):
        """ It should call the adapter methods with proper args """
        expect = ('query', 'execute', 'metadata')
        return_value = 'rows', 'cols'
        res, adapter = self._test_adapter_method(
            'execute', args=expect, return_value=return_value,
        )
        adapter.assert_called_once_with(*expect)

    def test_execute_return(self):
        """ It should return rows if not metadata """
        expect = (True, True, False)
        return_value = 'rows', 'cols'
        res, adapter = self._test_adapter_method(
            'execute', args=expect, return_value=return_value,
        )
        self.assertEqual(res, return_value[0])

    def test_execute_return_metadata(self):
        """ It should return rows and cols if metadata """
        expect = (True, True, True)
        return_value = 'rows', 'cols'
        res, adapter = self._test_adapter_method(
            'execute', args=expect, return_value=return_value,
        )
        self.assertEqual(
            res,
            {'rows': return_value[0],
             'cols': return_value[1]},
        )

    def test_remote_browse(self):
        """ It should call the adapter method with proper args """
        args = [1], 'args'
        kwargs = {'kwargs': True}
        self.dbsource.current_table = 'table'
        res, adapter = self._test_adapter_method(
            'remote_browse', create=True, args=args, kwargs=kwargs,
        )
        adapter.assert_called_once_with(*args, **kwargs)
        self.assertEqual(res, adapter())

    def test_remote_browse_asserts_current_table(self):
        """ It should raise AssertionError if a table is not selected """
        args = [1], 'args'
        kwargs = {'kwargs': True}
        with self.assertRaises(AssertionError):
            res, adapter = self._test_adapter_method(
                'remote_browse', create=True, args=args, kwargs=kwargs,
            )

    def test_remote_create(self):
        """ It should call the adapter method with proper args """
        args = {'val': 'Value'}, 'args'
        kwargs = {'kwargs': True}
        self.dbsource.current_table = 'table'
        res, adapter = self._test_adapter_method(
            'remote_create', create=True, args=args, kwargs=kwargs,
        )
        adapter.assert_called_once_with(*args, **kwargs)
        self.assertEqual(res, adapter())

    def test_remote_create_asserts_current_table(self):
        """ It should raise AssertionError if a table is not selected """
        args = [1], 'args'
        kwargs = {'kwargs': True}
        with self.assertRaises(AssertionError):
            res, adapter = self._test_adapter_method(
                'remote_create', create=True, args=args, kwargs=kwargs,
            )

    def test_remote_delete(self):
        """ It should call the adapter method with proper args """
        args = [1], 'args'
        kwargs = {'kwargs': True}
        self.dbsource.current_table = 'table'
        res, adapter = self._test_adapter_method(
            'remote_delete', create=True, args=args, kwargs=kwargs,
        )
        adapter.assert_called_once_with(*args, **kwargs)
        self.assertEqual(res, adapter())

    def test_remote_delete_asserts_current_table(self):
        """ It should raise AssertionError if a table is not selected """
        args = [1], 'args'
        kwargs = {'kwargs': True}
        with self.assertRaises(AssertionError):
            res, adapter = self._test_adapter_method(
                'remote_delete', create=True, args=args, kwargs=kwargs,
            )

    def test_remote_search(self):
        """ It should call the adapter method with proper args """
        args = {'search': 'query'}, 'args'
        kwargs = {'kwargs': True}
        self.dbsource.current_table = 'table'
        res, adapter = self._test_adapter_method(
            'remote_search', create=True, args=args, kwargs=kwargs,
        )
        adapter.assert_called_once_with(*args, **kwargs)
        self.assertEqual(res, adapter())

    def test_remote_search_asserts_current_table(self):
        """ It should raise AssertionError if a table is not selected """
        args = [1], 'args'
        kwargs = {'kwargs': True}
        with self.assertRaises(AssertionError):
            res, adapter = self._test_adapter_method(
                'remote_search', create=True, args=args, kwargs=kwargs,
            )

    def test_remote_update(self):
        """ It should call the adapter method with proper args """
        args = [1], {'vals': 'Value'}, 'args'
        kwargs = {'kwargs': True}
        self.dbsource.current_table = 'table'
        res, adapter = self._test_adapter_method(
            'remote_update', create=True, args=args, kwargs=kwargs,
        )
        adapter.assert_called_once_with(*args, **kwargs)
        self.assertEqual(res, adapter())

    def test_remote_update_asserts_current_table(self):
        """ It should raise AssertionError if a table is not selected """
        args = [1], 'args'
        kwargs = {'kwargs': True}
        with self.assertRaises(AssertionError):
            res, adapter = self._test_adapter_method(
                'remote_update', create=True, args=args, kwargs=kwargs,
            )

    # Postgres

    def test_execute_postgresql(self):
        """ It should call generic executor with proper args """
        expect = ('query', 'execute', 'metadata')
        with mock.patch.object(
            self.dbsource, '_execute_generic', autospec=True,
        ) as execute:
            execute.return_value = 'rows', 'cols'
            self.dbsource.execute(*expect)
            execute.assert_called_once_with(*expect)

    # Old API Compat

    def test_execute_calls_adapter_old_api(self):
        """ It should call the adapter correctly if old kwargs provided """
        expect = [None, None, 'metadata']
        with mock.patch.object(
            self.dbsource, 'execute_postgresql', autospec=True,
        ) as psql:
            psql.return_value = 'rows', 'cols'
            self.dbsource.execute(
                *expect, sqlparams='params', sqlquery='query'
            )
            expect[0], expect[1] = 'query', 'params'
            psql.assert_called_once_with(*expect)

    def test_conn_open(self):
        """ It should return open connection for use """
        with mock.patch.object(
            self.dbsource, 'connection_open', autospec=True,
        ) as connection:
            res = self.dbsource.conn_open()
            self.assertEqual(
                res,
                connection().__enter__(),
            )
