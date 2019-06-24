# coding: utf-8
# @ 2015 Valentin CHEMIERE @ Akretion
# ©2016 @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from base64 import b64decode
import hashlib
from .common import TestConnection, ContextualStringIO
from .mock_server import server_mock_sftp
from .mock_server import MultiResponse
from openerp.exceptions import UserError


_logger = logging.getLogger(__name__)


class TestSftpConnection(TestConnection):

    def setUp(self):
        super(TestSftpConnection, self).setUp()
        self.test_file_sftp = ContextualStringIO()
        self.test_file_sftp.write('import sftp')
        self.test_file_sftp.seek(0)

    def test_00_sftp_import(self):
        task = self.env.ref('external_file_location.sftp_import_task')
        with server_mock_sftp(
                {'open': self.test_file_sftp,
                 'listdir': [task.filename]}):
            task.run_import()
        search_file = self.env['ir.attachment.metadata'].search(
            [('name', '=', task.filename)])
        self.assertEqual(len(search_file), 1)
        self.assertEqual(b64decode(search_file[0].datas), 'import sftp')

    def test_01_sftp_export(self):
        self.task = self.env.ref('external_file_location.sftp_export_task')
        self.sftp_attachment = self.env.ref(
            'external_file_location.ir_attachment_export_file_sftp')
        with server_mock_sftp(
                {'setcontents': ''}) as FakeSFTP:
            self.task.run_export()
            if FakeSFTP:
                self.assertEqual('setcontents', FakeSFTP[-1]['method'])
                self.assertEqual(
                    '/home/user/test/sftp_test_export.txt',
                    FakeSFTP[-1]['args'][0])
                self.assertEqual(
                    'test sftp file export',
                    FakeSFTP[-1]['kwargs']['data'])

    def test_02_sftp_import_md5(self):
        md5_file = ContextualStringIO()
        md5_file.write(hashlib.md5('import sftp').hexdigest())
        md5_file.seek(0)
        task = self.env.ref('external_file_location.sftp_import_task')
        task.md5_check = True
        with server_mock_sftp(
                {'open': MultiResponse({
                    1: md5_file,
                    0: self.test_file_sftp}),
                 'listdir': [task.filename]}) as FakeSFTP:
            task.run_import()
            search_file = self.env['ir.attachment.metadata'].search(
                (('name', '=', task.filename),))
            self.assertEqual(len(search_file), 1)
            self.assertEqual(b64decode(search_file[0].datas),
                             'import sftp')
            self.assertEqual('open', FakeSFTP[-1]['method'])
            self.assertEqual(hashlib.md5('import sftp').hexdigest(),
                             search_file.external_hash)

    def test_03_sftp_import_md5_corrupt_file(self):
        md5_file = ContextualStringIO()
        md5_file.write(hashlib.md5('import test sftp corrupted').hexdigest())
        md5_file.seek(0)
        task = self.env.ref('external_file_location.sftp_import_task')
        task.md5_check = True
        with server_mock_sftp(
                {'open': MultiResponse({
                    1: md5_file,
                    0: self.test_file_sftp}),
                 'listdir': [task.filename]}):
            with self.assertRaises(UserError):
                task.run_import()
