# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class DemoRemoteOk:
    def __init__(self, target, data, auth):
        self.target = target
        self.data = data
        self.auth = auth

    ok = True


class DemoRemoteFailure:
    def __init__(self, target, data, auth):
        self.target = target
        self.data = data
        self.auth = auth

    ok = False


class TestNagios(TransactionCase):

    def test_nagios(self):
        nagios = self.env['nagios.server'].create({
            'name': 'Test',
            'target': 'http://localhost/nagios/cgi-bin/cmd.cgi',
            'host': 'odoodev',
            'service': 'testing',
        })
        with mock.patch('requests.post') as post:
            post.return_value = DemoRemoteOk
            nagios.send()
            post.assert_called_once()
            args, kwargs = post.call_args
            self.assertEqual(args[0], nagios.target)
            self.assertFalse(kwargs['auth'])

    def test_nagios_failure(self):
        nagios = self.env['nagios.server'].create({
            'name': 'Test',
            'target': 'http://localhost/nagios/cgi-bin/cmd.cgi',
            'host': 'odoodev',
            'service': 'testing',
        })
        with mock.patch('requests.post') as post:
            post.return_value = DemoRemoteFailure
            with self.assertRaises(UserError):
                nagios.send()
            post.assert_called_once()
            args, kwargs = post.call_args
            self.assertEqual(args[0], nagios.target)
            self.assertFalse(kwargs['auth'])

    def test_nagios_cron(self):
        nagios = self.env['nagios.server'].create({
            'name': 'Test',
            'target': 'http://localhost/nagios/cgi-bin/cmd.cgi',
            'host': 'odoodev',
            'service': 'testing',
            'requires_authentication': True,
            'authentication_user': 'user',
            'authentication_password': 'pass',
        })
        with mock.patch('requests.post') as post:
            post.return_value = DemoRemoteOk
            nagios._cron_send([('id', '=', nagios.id)])
            post.assert_called_once()
            args, kwargs = post.call_args
            self.assertEqual(args[0], nagios.target)
            self.assertEqual(kwargs['auth'], ('user', 'pass'))
