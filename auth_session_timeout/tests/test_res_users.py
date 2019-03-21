# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock

from contextlib import contextmanager

from odoo.tools.misc import mute_logger
from odoo.tests.common import TransactionCase


class EndTestException(Exception):
    """ It stops tests from continuing """
    pass


class TestResUsers(TransactionCase):

    post_install = True
    at_install = False

    def setUp(self):
        super(TestResUsers, self).setUp()
        self.TestUser = self.env['res.users'].create({
            'login': 'test_user',
            'name': 'test_user',
        })

    @contextmanager
    def _mock_assets(self, assets=None):
        """ Multi patch names in `odoo.addons.auth_session_timeout.models.
        res_users` for mocking them.

        :param assets: The symbols in res_users that will be patched with
        MagicMock objects.
        """
        if assets is None:
            assets = ['http']
        patches = {name: mock.DEFAULT for name in assets}
        with mock.patch.multiple(
            'odoo.addons.auth_session_timeout.models.res_users', **patches
        ) as mocks:
            yield mocks

    def _auth_timeout_check(self, http_mock):
        """ It wraps ``_auth_timeout_check`` for easier calling """
        self.db = mock.MagicMock()
        self.uid = mock.MagicMock()
        self.passwd = mock.MagicMock()
        self.path = '/this/is/a/test/path'
        get_filename = http_mock.root.session_store.get_session_filename
        get_filename.return_value = self.path
        return self.TestUser._auth_timeout_check()

    def test_session_validity_no_request(self):
        """ Tests what happens when the user being tested has not made any
        requests.
        """
        with self._mock_assets() as assets:
            assets['http'].request = False
            res = self._auth_timeout_check(assets['http'])
            self.assertFalse(res)

    def test_session_validity_gets_session_file(self):
        """ All the sessions a user generates are saved as a file in the
        filesystem by Werkzeug.

        This function makes sure that our `_auth_timeout_check` makes an
        attempt in fetching that file by the correct session id.
        """
        with self._mock_assets() as assets:
            store = assets['http'].root.session_store
            store.get_session_filename.side_effect = EndTestException
            with self.assertRaises(EndTestException):
                self._auth_timeout_check(assets['http'])
            store.get_session_filename.assert_called_once_with(
                assets['http'].request.session.sid,
            )

    def test_session_validity_logout(self):
        """ Forcefully expire an already existing session and see if the user
        is actually logged out.
        """
        with self._mock_assets(['http', 'getmtime', 'utime']) as assets:
            assets['getmtime'].return_value = 0
            self._auth_timeout_check(assets['http'])
            assets['http'].request.session.logout.assert_called_once_with(
                keep_db=True,
            )

    def test_session_validity_updates_utime(self):
        """ When a user makes a request, `_auth_timeout_check` is keeping the
        user's time of request by setting the access time of the session file
        using utime.

        This function asserts that the access time of the session file is set
        correctly.
        """
        with self._mock_assets(['http', 'getmtime', 'utime']) as assets:
            self._auth_timeout_check(assets['http'])
            assets['utime'].assert_called_once_with(
                assets['http'].root.session_store.get_session_filename(),
                None,
            )

    @mute_logger('odoo.addons.auth_session_timeout.models.res_users')
    def test_session_validity_os_error_guard(self):
        """ Make sure that when we get an OSError while trying to set up an
        access time the session is terminated immediately.
        """
        with self._mock_assets(['http', 'utime', 'getmtime']) as assets:
            assets['getmtime'].side_effect = OSError
            res = self._auth_timeout_check(assets['http'])
            self.assertFalse(res)

    def test_on_timeout_session_loggedout(self):
        """ Make sure that when the timeout has come, the user is actually
        logged out.
        """
        with self._mock_assets(['http', 'getmtime']) as assets:
            assets['getmtime'].return_value = 0
            assets['http'].request.env.user = self.TestUser
            assets['http'].request.session.uid = self.TestUser.id
            assets['http'].request.session.dbname = self.env.cr.dbname
            assets['http'].request.session.sid = '123'
            assets['http'].request.session.logout = mock.Mock()
            self.TestUser._compute_session_token('123')
            self.assertTrue(assets['http'].request.session.logout.called)
