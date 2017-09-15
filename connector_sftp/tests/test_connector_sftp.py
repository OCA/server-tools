# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
import mock


paramiko = 'odoo.addons.connector_sftp.models.connector_sftp.paramiko'


class TestConnectorSftp(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestConnectorSftp, self).setUp(*args, **kwargs)
        self.model_obj = self.env['connector.sftp']
        self.vals = {
            'name': 'Test',
            'host': 'example.com',
            'port': 22,
            'username': 'test',
            'password': 'pass',
            'host_key': 'hostkey',
            'private_key': 'privatekey',
            'company_id': self.env.user.company_id.id,
        }

    def _new_record(self, ):
        return self.model_obj.create(self.vals)

    @mock.patch(paramiko)
    def test_compute_client_initializes_transport(self, mk):
        rec_id = self._new_record()
        rec_id._compute_client_and_transport()
        mk.Transport.assert_called_once_with((
            self.vals['host'], self.vals['port']
        ))

    @mock.patch(paramiko)
    def test_compute_client_connects_to_transport(self, mk):
        rec_id = self._new_record()
        rec_id._compute_client_and_transport()
        mk.Transport().connect.assert_called_once_with(
            hostkey=self.vals['host_key'],
            username=self.vals['username'],
            password=self.vals['password'],
            pkey=self.vals['private_key'],
        )

    @mock.patch(paramiko)
    def test_compute_client_connects_to_transport_with_no_key(self, mk):
        del self.vals['private_key']
        rec_id = self._new_record()
        rec_id._compute_client_and_transport()
        mk.Transport().connect.assert_called_once_with(
            hostkey=self.vals['host_key'],
            username=self.vals['username'],
            password=self.vals['password'],
            pkey=None,
        )

    @mock.patch(paramiko)
    def test_compute_client_connects_to_transport_with_no_hostkey(self, mk):
        del self.vals['host_key']
        rec_id = self._new_record()
        rec_id._compute_client_and_transport()
        mk.Transport().connect.assert_called_once_with(
            hostkey=None,
            username=self.vals['username'],
            password=self.vals['password'],
            pkey=self.vals['private_key'],
        )

    @mock.patch(paramiko)
    def test_compute_client_obeys_ignore_hostkey(self, mk):
        self.vals['ignore_host_key'] = True
        rec_id = self._new_record()
        rec_id._compute_client_and_transport()
        mk.Transport().connect.assert_called_once_with(
            hostkey=None,
            username=self.vals['username'],
            password=self.vals['password'],
            pkey=self.vals['private_key'],
        )

    @mock.patch(paramiko)
    def test_compute_client_inits_sftp_client(self, mk):
        rec_id = self._new_record()
        rec_id._compute_client_and_transport()
        mk.SFTPClient.from_transport.assert_called_once_with(
            mk.Transport()
        )

    @mock.patch(paramiko)
    def test_list_dir(self, _):
        rec_id = self._new_record()
        expect = 'Test'
        rec_id.list_dir(expect)
        rec_id.client.listdir.assert_called_once_with(expect)

    @mock.patch(paramiko)
    def test_stat(self, _):
        rec_id = self._new_record()
        expect = 'Test'
        rec_id.stat(expect)
        rec_id.client.stat.assert_called_once_with(expect)

    @mock.patch(paramiko)
    def test_open(self, _):
        rec_id = self._new_record()
        expect = 'Test', 'w', 1
        rec_id.open(*expect)
        rec_id.client.open.assert_called_once_with(*expect)

    @mock.patch(paramiko)
    def test_delete(self, _):
        rec_id = self._new_record()
        expect = 'Test'
        rec_id.delete(expect)
        rec_id.client.unlink.assert_called_once_with(expect)

    @mock.patch(paramiko)
    def test_symlink(self, _):
        rec_id = self._new_record()
        expect = 'Test', 'Dest'
        rec_id.symlink(*expect)
        rec_id.client.symlink.assert_called_once_with(*expect)
