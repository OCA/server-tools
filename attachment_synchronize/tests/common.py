# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo.tests.common import TransactionCase


class SyncCommon(TransactionCase):
    def _clean_testing_directory(self):
        for test_dir in [
            self.directory_input,
            self.directory_output,
            self.directory_archived,
        ]:
            fs = self.backend.fs
            if not fs.exists(test_dir):
                fs.makedirs(test_dir)
            for filename in fs.ls(test_dir, detail=False):
                fs.rm(filename)

    def _create_test_file(self):
        fs = self.backend.fs
        path = fs.sep.join([self.directory_input, "bar.txt"])
        with fs.open(path, "wb") as f:
            f.write(self.filedata)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend = cls.env.ref("fs_storage.fs_storage_demo")
        cls.filedata = base64.b64encode(b"This is a simple file")
        cls.directory_input = "test_import"
        cls.directory_output = "test_export"
        cls.directory_archived = "test_archived"
        cls.task = cls.env.ref("attachment_synchronize.import_from_filestore")
        cls.task_delete = cls.env.ref(
            "attachment_synchronize.import_from_filestore_delete"
        )
        cls.task_move = cls.env.ref("attachment_synchronize.import_from_filestore_move")
        cls.task_rename = cls.env.ref(
            "attachment_synchronize.import_from_filestore_rename"
        )
        cls.task_move_rename = cls.env.ref(
            "attachment_synchronize.import_from_filestore_move_rename"
        )

    def setUp(self):
        super().setUp()
        self._clean_testing_directory()
        self._create_test_file()

    def tearDown(self):
        self._clean_testing_directory()
        super().tearDown()
