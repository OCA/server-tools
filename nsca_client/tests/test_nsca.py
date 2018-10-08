# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock

from odoo.tests.common import TransactionCase


class Popen:
    def __init__(self, cmd, stdout, stdin, stderr):
        self.cmd = cmd
        self.stdout = stdout
        self.stdin = stdin
        self.stderr = stderr

    def communicate(input):
        return ['test']


class TestNsca(TransactionCase):

    def test_nsca(self):
        server = self.env['nsca.server'].create({
            'name': 'localhost',
            'password': 'pass',
            'encryption_method': '3',
            'node_hostname': 'odoodev',
        })
        self.assertTrue(server.config_file_path)
        with mock.patch('subprocess.Popen') as post:
            post.return_value = Popen
            check = self.env['nsca.check'].create({
                'server_id': server.id,
                'service': 'test',
                'nsca_model': 'nsca.server',
                'nsca_function': 'current_status'
            })
            self.assertTrue(check.model_id)
            self.env['nsca.check']._cron_check(check.id,)

    def test_write(self):
        server = self.env['nsca.server'].create({
            'name': 'localhost',
            'password': 'pass',
            'encryption_method': '3',
            'node_hostname': 'odoodev',
        })
        self.assertTrue(server.config_file_path)
        check = self.env['nsca.check'].create({
            'server_id': server.id,
            'service': 'test',
            'nsca_model': 'nsca.server',
            'nsca_function': 'current_status'
        })
        check.cron_id.state = 'object_create'
        check.write({'interval_number': 1})
        self.assertEqual(check.cron_id.state, 'object_create')
        check.write({'service': 'change'})
        self.assertNotEqual(check.cron_id.state, 'object_create')

    def test_void_failure(self):
        server = self.env['nsca.server'].create({
            'name': 'localhost',
            'password': 'pass',
            'encryption_method': '3',
            'node_hostname': 'odoodev',
        })
        check = self.env['nsca.check'].create({
            'server_id': server.id,
            'service': 'test',
            'nsca_model': 'nsca.server',
            'allow_void_result': False,
            'nsca_function': '_check_send_nsca_command'
        })
        with mock.patch('subprocess.Popen') as post:
            post.return_value = Popen
            self.env['nsca.check']._cron_check(check.id,)
            post.assert_called_once()

    def test_void_ok(self):
        server = self.env['nsca.server'].create({
            'name': 'localhost',
            'password': 'pass',
            'encryption_method': '3',
            'node_hostname': 'odoodev',
        })
        self.assertEqual(server.check_count, 0)
        check = self.env['nsca.check'].create({
            'server_id': server.id,
            'service': 'test',
            'nsca_model': 'nsca.server',
            'allow_void_result': True,
            'nsca_function': '_check_send_nsca_command'
        })
        self.assertEqual(server.check_count, 1)
        action = server.show_checks()
        self.assertEqual(check, self.env['nsca.check'].browse(
            action['res_id']))
        self.assertEqual(check, self.env['nsca.check'].search(
            action['domain']))
        with mock.patch('subprocess.Popen') as post:
            post.return_value = Popen
            self.env['nsca.check']._cron_check(check.id,)
            post.assert_not_called()
