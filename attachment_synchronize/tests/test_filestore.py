# coding: utf-8
# @ 2015 Valentin CHEMIERE @ Akretion
# ©2016 @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from base64 import b64decode
from .common import TestConnection, ContextualStringIO
from .mock_server import server_mock_filestore


_logger = logging.getLogger(__name__)


class TestfilestoreConnection(TestConnection):

    def setUp(self):
        super(TestfilestoreConnection, self).setUp()
        self.test_file_filestore = ContextualStringIO()
        self.test_file_filestore.write('import filestore')
        self.test_file_filestore.seek(0)

    def test_00_filestore_import(self):
        self.task = self.env.ref(
            'external_file_location.filestore_import_task')
        with server_mock_filestore(
                {'open': self.test_file_filestore,
                 'listdir': ['test-import-filestore.txt']}):
            self.task.run_import()
        search_file = self.env['ir.attachment.metadata'].search(
            [('name', '=', 'test-import-filestore.txt')])
        self.assertEqual(len(search_file), 1)
        self.assertEqual(b64decode(search_file[0].datas), 'import filestore')

    def test_01_filestore_export(self):
        self.task = self.env.ref(
            'external_file_location.filestore_export_task')
        self.filestore_attachment = self.env.ref(
            'external_file_location.ir_attachment_export_file_filestore')
        with server_mock_filestore(
                {'setcontents': ''}) as Fakefilestore:
            self.task.run_export()
            if Fakefilestore:
                self.assertEqual('setcontents', Fakefilestore[-1]['method'])
                self.assertEqual('done', self.filestore_attachment.state)
                self.assertEqual(
                    '/home/user/test/filestore_test_export.txt',
                    Fakefilestore[-1]['args'][0])
                self.assertEqual(
                    'test filestore file export',
                    Fakefilestore[-1]['kwargs']['data'])
