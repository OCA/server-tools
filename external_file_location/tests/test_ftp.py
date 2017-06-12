# coding: utf-8
# @ 2015 Valentin CHEMIERE @ Akretion
# ©2016 @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from base64 import b64decode
import hashlib
from .common import TestConnection, ContextualStringIO
from .mock_server import server_mock_ftp
from .mock_server import MultiResponse
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class TestFtpConnection(TestConnection):

    def setUp(self):
        super(TestFtpConnection, self).setUp()
        self.test_file_ftp = ContextualStringIO()
        self.test_file_ftp.write('import ftp')
        self.test_file_ftp.seek(0)

    def test_00_ftp_import(self):
        self.task = self.env.ref('external_file_location.ftp_import_task')
        with server_mock_ftp(
                {'open': self.test_file_ftp,
                 'listdir': ['test-import-ftp.txt']}):
            self.task.run_import()
        search_file = self.env['ir.attachment.metadata'].search(
            [('name', '=', 'test-import-ftp.txt')])
        self.assertEqual(len(search_file), 1)
        self.assertEqual(b64decode(search_file[0].datas), 'import ftp')

    def test_01_ftp_export(self):
        self.task = self.env.ref('external_file_location.ftp_export_task')
        self.ftp_attachment = self.env.ref(
            'external_file_location.ir_attachment_export_file_ftp')
        with server_mock_ftp(
                {'setcontents': ''}) as FakeFTP:
            self.task.run_export()
            if FakeFTP:
                self.assertEqual('setcontents', FakeFTP[-1]['method'])
                self.assertEqual('done', self.ftp_attachment.state)
                self.assertEqual(
                    '/home/user/test/ftp_test_export.txt',
                    FakeFTP[-1]['args'][0])
                self.assertEqual(
                    'test ftp file export',
                    FakeFTP[-1]['kwargs']['data'])

    def test_02_ftp_import_md5(self):
        md5_file = ContextualStringIO()
        md5_file.write(hashlib.md5('import ftp').hexdigest())
        md5_file.seek(0)
        task = self.env.ref('external_file_location.ftp_import_task')
        task.md5_check = True
        with server_mock_ftp(
                {'open': MultiResponse({
                    1: md5_file,
                    0: self.test_file_ftp}),
                 'listdir': [task.filename]}) as Fakeftp:
            task.run_import()
            search_file = self.env['ir.attachment.metadata'].search(
                (('name', '=', task.filename),))
            self.assertEqual(len(search_file), 1)
            self.assertEqual(b64decode(search_file[0].datas),
                             'import ftp')
            self.assertEqual('open', Fakeftp[-1]['method'])
            self.assertEqual(hashlib.md5('import ftp').hexdigest(),
                             search_file.external_hash)

    def test_03_ftp_import_md5_corrupt_file(self):
        md5_file = ContextualStringIO()
        md5_file.write(hashlib.md5('import test ftp corrupted').hexdigest())
        md5_file.seek(0)
        task = self.env.ref('external_file_location.ftp_import_task')
        task.md5_check = True
        with server_mock_ftp(
                {'open': MultiResponse({
                    1: md5_file,
                    0: self.test_file_ftp}),
                 'listdir': [task.filename]}):
            with self.assertRaises(UserError):
                task.run_import()
