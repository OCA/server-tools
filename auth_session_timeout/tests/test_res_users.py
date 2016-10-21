# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock

from contextlib import contextmanager

from odoo.tests.common import TransactionCase


class EndTestException(Exception):
    """ It stops tests from continuing """
    pass


class TestResUsers(TransactionCase):

    def setUp(self):
        super(TestResUsers, self).setUp()
        self.ResUsers = self.env['res.users']

    @contextmanager
    def _mock_assets(self, assets=None):
        """ It provides mocked imports from res_users.py
        :param assets: (list) Name of imports to mock. Mocks `http` if None
        :return: (dict) Dictionary of mocks, keyed by module name
        """
        if assets is None:
            assets = ['http']
        patches = {name: mock.DEFAULT for name in assets}
        with mock.patch.multiple(
            'odoo.addons.auth_session_timeout.models.res_users', **patches
        ) as mocks:
            yield mocks

    def _check_session_validity(self):
        """ It wraps ``_check_session_validity`` for easier calling """
        self.db = mock.MagicMock()
        self.uid = mock.MagicMock()
        self.passwd = mock.MagicMock()
        return self.ResUsers._check_session_validity(
            self.db, self.uid, self.passwd,
        )

    def test_session_validity_no_request(self):
        """ It should return immediately if no request """
        with self._mock_assets() as assets:
            assets['http'].request = False
            res = self._check_session_validity()
            self.assertFalse(res)

    def test_session_validity_gets_params(self):
        """ It should call ``get_session_parameters`` with db """
        with self._mock_assets() as assets:
            get_params = assets['http'].request.env[''].get_session_parameters
            get_params.side_effect = EndTestException
            with self.assertRaises(EndTestException):
                self._check_session_validity()
            get_params.assert_called_once_with()

    def test_session_validity_gets_session_file(self):
        """ It should call get the session file for the session id """
        with self._mock_assets() as assets:
            get_params = assets['http'].request.env[''].get_session_parameters
            get_params.return_value = 0, []
            store = assets['http'].root.session_store
            store.get_session_filename.side_effect = EndTestException
            with self.assertRaises(EndTestException):
                self._check_session_validity()
            store.get_session_filename.assert_called_once_with(
                assets['http'].request.session.sid,
            )

    def test_session_validity_logout(self):
        """ It should log out of session if past deadline """
        with self._mock_assets(['http', 'getmtime', 'utime']) as assets:
            get_params = assets['http'].request.env[''].get_session_parameters
            get_params.return_value = -9999, []
            assets['getmtime'].return_value = 0
            self._check_session_validity()
            assets['http'].request.session.logout.assert_called_once_with(
                keep_db=True,
            )

    def test_session_validity_updates_utime(self):
        """ It should update utime of session file if not expired """
        with self._mock_assets(['http', 'getmtime', 'utime']) as assets:
            get_params = assets['http'].request.env[''].get_session_parameters
            get_params.return_value = 9999, []
            self._check_session_validity()
            assets['utime'].assert_called_once_with(
                assets['http'].root.session_store.get_session_filename(),
                None,
            )

    def test_session_validity_os_error_guard(self):
        """ It should properly guard from OSError & return """
        with self._mock_assets(['http', 'utime', 'getmtime']) as assets:
            get_params = assets['http'].request.env[''].get_session_parameters
            get_params.return_value = 0, []
            assets['getmtime'].side_effect = OSError
            res = self._check_session_validity()
            self.assertFalse(res)
