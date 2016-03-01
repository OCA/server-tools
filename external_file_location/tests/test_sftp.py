# coding: utf-8
# @ 2015 Valentin CHEMIERE @ Akretion
# ©2016 @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from StringIO import StringIO
from base64 import b64decode
import hashlib

import openerp.tests.common as common
from ..tasks.sftp import SftpImportTask
from ..tasks.sftp import SftpExportTask
from .mock_server import (server_mock)
from .mock_server import MultiResponse


_logger = logging.getLogger(__name__)


class ContextualStringIO(StringIO):
    """
    snippet from http://bit.ly/1HfH6uW (stackoverflow)
    """

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
        return False


class TestNewSource(common.TransactionCase):
    def setUp(self):
        super(TestNewSource, self).setUp()
        self.test_file = ContextualStringIO()
        self.test_file.write('import')
        self.test_file.seek(0)
        self.config = \
            {'file_name': 'testfile',
             'user': 'test',
             'password': 'test',
             'host': 'test',
             'port': 22,
             'attachment_ids': self.env['ir.attachment.metadata'].browse(False)
             }

    def test_00_sftp_import(self):
        with server_mock(
            {'exists': True,
             'makedir': True,
             'open': self.test_file,
             'listdir': ['testfile']
             }):
            task = SftpImportTask(self.env, self.config)
            task.run()
        search_file = self.env['ir.attachment.metadata'].search(
            (('name', '=', 'testfile'),))
        self.assertEqual(len(search_file), 1)
        self.assertEqual(b64decode(search_file[0].datas), 'import')

    def test_01_sftp_export(self):
        with server_mock(
            {'isfile': False,
             'open': self.test_file,
             }) as FakeSFTP:
            task = SftpExportTask(self.env, self.config)
            task.run()
            if FakeSFTP:
                self.assertEqual('open', FakeSFTP[-1]['method'])

    def test_02_sftp_import_delete(self):
        with server_mock(
            {'exists': True,
             'makedir': True,
             'open': self.test_file,
             'listdir': ['testfile'],
             'remove': True
             }) as FakeSFTP:
            self.config.update({'after_import': 'delete'})
            task = SftpImportTask(self.env, self.config)
            task.run()
            search_file = self.env['ir.attachment.metadata'].search(
                (('name', '=', 'testfile'),))
            self.assertEqual(len(search_file), 1)
            self.assertEqual(b64decode(search_file[0].datas), 'import')
            self.assertEqual('remove', FakeSFTP[-1]['method'])
            self.assertEqual(
                './testfile', FakeSFTP[-1]['args'][0],
                "Delete File must be './testfile'")

    def test_03_sftp_import_move(self):
        with server_mock(
            {'exists': True,
             'makedir': True,
             'open': self.test_file,
             'listdir': ['testfile'],
             'rename': True
             }) as FakeSFTP:
            self.config.update({'after_import': 'move', 'move_path': '/home'})
            task = SftpImportTask(self.env, self.config)
            task.run()
            search_file = self.env['ir.attachment.metadata'].search(
                (('name', '=', 'testfile'),))
            self.assertEqual(len(search_file), 1)
            self.assertEqual(b64decode(search_file[0].datas), 'import')
            self.assertEqual('rename', FakeSFTP[-1]['method'])

    def test_04_sftp_import_rename(self):
        with server_mock(
            {'exists': True,
             'makedir': True,
             'open': self.test_file,
             'listdir': ['testfile'],
             'rename': True
             }) as FakeSFTP:
            _logger.info("Test sftp rename file")
            self.config.update({
                'after_import': 'rename',
                'new_name': '${obj.name}.imported',
                'path': '/home',
                })
            task = SftpImportTask(self.env, self.config)
            task.run()
            search_file = self.env['ir.attachment.metadata'].search(
                (('name', '=', 'testfile'),))
            self.assertEqual(len(search_file), 1)
            self.assertEqual(b64decode(search_file[0].datas), 'import')
            self.assertEqual('rename', FakeSFTP[2]['method'])
            self.assertEqual('/home/testfile.imported',
                             FakeSFTP[2]['args'][1],
                             "File not renamed")

    def test_05_sftp_import_move_rename(self):
        with server_mock(
            {'exists': True,
             'makedir': True,
             'open': self.test_file,
             'listdir': ['testfile'],
             'rename': True
             }) as FakeSFTP:
            _logger.info("Test sftp move and rename file")
            self.config.update({
                'after_import': 'rename',
                'new_name': '${obj.name}.imported',
                'path': '/home',
                'move_path': '/home/processed',
                })
            task = SftpImportTask(self.env, self.config)
            task.run()
            search_file = self.env['ir.attachment.metadata'].search(
                (('name', '=', 'testfile'),))
            self.assertEqual(len(search_file), 1)
            self.assertEqual(b64decode(search_file[0].datas), 'import')
            self.assertEqual('rename', FakeSFTP[3]['method'])
            self.assertEqual('/home/processed/testfile.imported',
                             FakeSFTP[3]['args'][1],
                             "File not renamed and moved")

    def test_06_sftp_import_md5(self):
        md5_file = ContextualStringIO()
        md5_file.write(hashlib.md5('import').hexdigest())
        md5_file.seek(0)
        with server_mock(
            {'exists': True,
             'makedir': True,
             'open': MultiResponse({
                 1: self.test_file,
                 0: md5_file
             }),
             'listdir': ['testfile', 'testfile.md5'],
             }) as FakeSFTP:
            self.config.update({'md5_check': True})
            task = SftpImportTask(self.env, self.config)
            task.run()
            search_file = self.env['ir.attachment.metadata'].search(
                (('name', '=', 'testfile'),))
            self.assertEqual(len(search_file), 1)
            self.assertEqual(b64decode(search_file[0].datas), 'import')
            self.assertEqual('open', FakeSFTP[-1]['method'])
            self.assertEqual('open', FakeSFTP[1]['method'])
            self.assertEqual(('./testfile.md5', 'rb'), FakeSFTP[1]['args'])
