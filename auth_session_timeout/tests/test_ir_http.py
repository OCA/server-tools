# -*- coding: utf-8 -*-
# Copyright 2019 Anass Ahmed.

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock

from contextlib import contextmanager

from odoo.tests.common import TransactionCase


class TestIrHttp(TransactionCase):

    post_install = True
    at_install = False

    def setUp(self):
        super(TestIrHttp, self).setUp()
        self.TestUser = self.env['res.users'].create({
            'login': 'test_user',
            'name': 'test_user',
        })

    @contextmanager
    def _mock_assets(self, assets=None):
        """ Multi patch names in `odoo.addons.auth_session_timeout.models.
        ir_http` for mocking them.

        :param assets: The symbols in ir_http that will be patched with
        MagicMock objects.
        """
        if assets is None:
            assets = ['request']
        patches = {name: mock.DEFAULT for name in assets}
        with mock.patch.multiple(
            'odoo.addons.auth_session_timeout.models.ir_http', **patches
        ) as mocks:
            yield mocks

    def test_authenticate_check_timeout(self):
        """Make sure each time _authenticate is called, the timeout is
           checked."""
        with self._mock_assets() as assets:
            user = mock.MagicMock()
            assets['request'].env.user = user
            assets['request'].session.uid = 10
            assets['request'].session.dbname = self.env.cr.dbname
            assets['request'].session.sid = '123'
            with mock.patch('odoo.addons.base.ir.ir_http.IrHttp'
                            '._authenticate') as mock_super_athenticate:
                self.env['ir.http']._authenticate()
                self.assertTrue(mock_super_athenticate.called)
            self.assertTrue(user._auth_timeout_check.called)

    def test_initial_check_no_user(self):
        """Make sure _auth_timeout_check is not called when no user is stored
           in the session."""
        with self._mock_assets() as assets:
            user = mock.MagicMock()
            assets['request'].env.user = None
            assets['request'].session.uid = None
            assets['request'].session.dbname = self.env.cr.dbname
            assets['request'].session.sid = '123'
            with mock.patch('odoo.addons.base.ir.ir_http.IrHttp'
                            '._authenticate') as mock_super_athenticate:
                self.env['ir.http']._authenticate()
                self.assertTrue(mock_super_athenticate.called)
            self.assertFalse(user._auth_timeout_check.called)
