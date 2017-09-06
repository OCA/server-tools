# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock
from os import strerror
from errno import ENOENT

from openerp.tests import common


_packagepath = 'openerp.addons.auth_session_timeout'


class ResUsers(common.TransactionCase):
    def setUp(self):
        super(ResUsers, self).setUp()
        self.resusers_obj = self.env['res.users']

    @mock.patch(_packagepath + '.models.res_users.request')
    @mock.patch(_packagepath + '.models.res_users.root')
    @mock.patch(_packagepath + '.models.res_users.getmtime')
    def test_on_timeout_session_loggedout(self, mock_getmtime,
                                          mock_root, mock_request):
        mock_getmtime.return_value = 0
        mock_request.session.uid = self.env.uid
        mock_request.session.dbname = self.env.cr.dbname
        mock_request.session.sid = 123
        mock_request.session.logout = mock.Mock()
        self.resusers_obj._auth_timeout_check()
        self.assertTrue(mock_request.session.logout.called)

    @mock.patch(_packagepath + '.models.res_users.request')
    @mock.patch(_packagepath + '.models.res_users.root')
    @mock.patch(_packagepath + '.models.res_users.getmtime')
    @mock.patch(_packagepath + '.models.res_users.utime')
    def test_sessionfile_io_exceptions_managed(self, mock_utime, mock_getmtime,
                                               mock_root, mock_request):
        mock_getmtime.side_effect = OSError(
            ENOENT, strerror(ENOENT), 'non-existent-filename')
        mock_request.session.uid = self.env.uid
        mock_request.session.dbname = self.env.cr.dbname
        mock_request.session.sid = 123
        self.resusers_obj._auth_timeout_check()
