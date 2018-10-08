# Copyright 2015 Agile Business Group <http://www.agilebg.com>
# Copyright 2015 Alessio Gerace <alesiso.gerace@agilebg.com>
# Copyright 2016 Grupo ESOC Ingenieria de Servicios, S.L.U. - Jairo Llopis
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import os
from contextlib import contextmanager
from datetime import datetime, timedelta

import mock

from odoo import exceptions, tools
from odoo.tests import common

try:
    import pysftp
except ImportError:
    pass


model = 'odoo.addons.auto_backup.models.db_backup'


class TestConnectionException(pysftp.ConnectionException):
    def __init__(self):
        super(TestConnectionException, self).__init__('test', 'test')


class TestDbBackup(common.TransactionCase):

    def setUp(self):
        super(TestDbBackup, self).setUp()
        self.Model = self.env["db.backup"]

    @contextmanager
    def mock_assets(self):
        """ It provides mocked core assets """
        self.path_join_val = '/this/is/a/path'
        with mock.patch('%s.db' % model) as db:
            with mock.patch('%s.os' % model) as os:
                with mock.patch('%s.shutil' % model) as shutil:
                    os.path.join.return_value = self.path_join_val
                    yield {
                        'db': db,
                        'os': os,
                        'shutil': shutil,
                    }

    @contextmanager
    def patch_filtered_sftp(self, record, mocks=None):
        """ It patches filtered record and provides a mock """
        if mocks is None:
            mocks = ['sftp_connection']
        mocks = {m: mock.DEFAULT for m in mocks}
        with mock.patch.object(record, 'filtered') as filtered:
            with mock.patch.object(record, 'backup_log'):
                with mock.patch.multiple(record, **mocks):
                    filtered.side_effect = [], [record]
                    yield filtered

    def new_record(self, method='sftp'):
        vals = {
            'name': u'Têst backup',
            'method': method,
        }
        if method == 'sftp':
            vals.update({
                'sftp_host': 'test_host',
                'sftp_port': '222',
                'sftp_user': 'tuser',
                'sftp_password': 'password',
                'folder': '/folder/',
            })
        self.vals = vals
        return self.Model.create(vals)

    def test_compute_name_sftp(self):
        """ It should create proper SFTP URI """
        rec_id = self.new_record()
        self.assertEqual(
            'sftp://%(user)s@%(host)s:%(port)s%(folder)s' % {
                'user': self.vals['sftp_user'],
                'host': self.vals['sftp_host'],
                'port': self.vals['sftp_port'],
                'folder': self.vals['folder'],
            },
            rec_id.name,
        )

    def test_check_folder(self):
        """ It should not allow recursive backups """
        rec_id = self.new_record('local')
        with self.assertRaises(exceptions.ValidationError):
            rec_id.write({
                'folder': '%s/another/path' % tools.config.filestore(
                    self.env.cr.dbname
                ),
            })

    @mock.patch('%s._' % model)
    def test_action_sftp_test_connection_success(self, _):
        """ It should raise connection succeeded warning """
        rec_id = self.new_record()
        with mock.patch.object(rec_id, 'sftp_connection'):
            with self.assertRaises(exceptions.Warning):
                rec_id.action_sftp_test_connection()
            _.assert_called_once_with("Connection Test Succeeded!")

    @mock.patch('%s._' % model)
    def test_action_sftp_test_connection_fail(self, _):
        """ It should raise connection fail warning """
        rec_id = self.new_record()
        with mock.patch.object(rec_id, 'sftp_connection') as conn:
            conn().__enter__.side_effect = TestConnectionException
            with self.assertRaises(exceptions.Warning):
                rec_id.action_sftp_test_connection()
            _.assert_called_once_with("Connection Test Failed!")

    def test_action_backup_local(self):
        """ It should backup local database """
        rec_id = self.new_record('local')
        filename = rec_id.filename(datetime.now())
        rec_id.action_backup()
        generated_backup = [f for f in os.listdir(rec_id.folder)
                            if f >= filename]
        self.assertEqual(1, len(generated_backup))

    def test_action_backup_local_cleanup(self):
        """ Backup local database and cleanup old databases """
        rec_id = self.new_record('local')
        rec_id.days_to_keep = 1
        old_date = datetime.now() - timedelta(days=3)
        filename = rec_id.filename(old_date)
        rec_id.action_backup()
        generated_backup = [f for f in os.listdir(rec_id.folder)
                            if f >= filename]
        self.assertEqual(2, len(generated_backup))

        filename = rec_id.filename(datetime.now())
        rec_id.action_backup()
        generated_backup = [f for f in os.listdir(rec_id.folder)
                            if f >= filename]
        self.assertEqual(1, len(generated_backup))

    def test_action_backup_sftp_mkdirs(self):
        """ It should create remote dirs """
        rec_id = self.new_record()
        with self.mock_assets():
            with self.patch_filtered_sftp(rec_id):
                conn = rec_id.sftp_connection().__enter__()
                rec_id.action_backup()
                conn.makedirs.assert_called_once_with(rec_id.folder)

    def test_action_backup_sftp_mkdirs_conn_exception(self):
        """ It should guard from ConnectionException on remote.mkdirs """
        rec_id = self.new_record()
        with self.mock_assets():
            with self.patch_filtered_sftp(rec_id):
                conn = rec_id.sftp_connection().__enter__()
                conn.makedirs.side_effect = TestConnectionException
                rec_id.action_backup()
                # No error was raised, test pass
                self.assertTrue(True)

    def test_action_backup_sftp_remote_open(self):
        """ It should open remote file w/ proper args """
        rec_id = self.new_record()
        with self.mock_assets() as assets:
            with self.patch_filtered_sftp(rec_id):
                conn = rec_id.sftp_connection().__enter__()
                rec_id.action_backup()
                conn.open.assert_called_once_with(
                    assets['os'].path.join(),
                    'wb'
                )

    def test_action_backup_all_search(self):
        """ It should search all records """
        rec_id = self.new_record()
        with mock.patch.object(rec_id, 'search'):
            rec_id.action_backup_all()
            rec_id.search.assert_called_once_with([])

    def test_action_backup_all_return(self):
        """ It should return result of backup operation """
        rec_id = self.new_record()
        with mock.patch.object(rec_id, 'search'):
            res = rec_id.action_backup_all()
            self.assertEqual(
                rec_id.search().action_backup(), res
            )

    @mock.patch('%s.pysftp' % model)
    def test_sftp_connection_init_passwd(self, pysftp):
        """ It should initiate SFTP connection w/ proper args and pass """
        rec_id = self.new_record()
        rec_id.sftp_connection()
        pysftp.Connection.assert_called_once_with(
            host=rec_id.sftp_host,
            username=rec_id.sftp_user,
            port=rec_id.sftp_port,
            password=rec_id.sftp_password,
        )

    @mock.patch('%s.pysftp' % model)
    def test_sftp_connection_init_key(self, pysftp):
        """ It should initiate SFTP connection w/ proper args and key """
        rec_id = self.new_record()
        rec_id.write({
            'sftp_private_key': 'pkey',
            'sftp_password': 'pkeypass',
        })
        rec_id.sftp_connection()
        pysftp.Connection.assert_called_once_with(
            host=rec_id.sftp_host,
            username=rec_id.sftp_user,
            port=rec_id.sftp_port,
            private_key=rec_id.sftp_private_key,
            private_key_pass=rec_id.sftp_password,
        )

    @mock.patch('%s.pysftp' % model)
    def test_sftp_connection_return(self, pysftp):
        """ It should return new sftp connection """
        rec_id = self.new_record()
        res = rec_id.sftp_connection()
        self.assertEqual(
            pysftp.Connection(), res,
        )

    def test_filename_default(self):
        """ It should not error and should return a .dump.zip file str """
        now = datetime.now()
        res = self.Model.filename(now)
        self.assertTrue(res.endswith(".dump.zip"))

    def test_filename_zip(self):
        """ It should return a dump.zip filename"""
        now = datetime.now()
        res = self.Model.filename(now, ext='zip')
        self.assertTrue(res.endswith(".dump.zip"))

    def test_filename_dump(self):
        """ It should return a dump filename"""
        now = datetime.now()
        res = self.Model.filename(now, ext='dump')
        self.assertTrue(res.endswith(".dump"))
