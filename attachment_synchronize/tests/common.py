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
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.filedata = base64.b64encode(b"This is a simple file")
        cls.directory_input = "test_import"
        cls.directory_output = "test_export"
        cls.directory_archived = "test_archived"
        # OCA CI does not load demo data; build fixtures inline.
        cls.backend = cls.env["fs.storage"].create(
            {
                "name": "Test Storage (attachment_synchronize)",
                "code": "attachment_synchronize_test",
                "protocol": "file",
                "directory_path": "/tmp/attachment_synchronize_test",
            }
        )
        AST = cls.env["attachment.synchronize.task"]
        common_vals = {"backend_id": cls.backend.id, "method_type": "import"}
        cls.task = AST.create(
            {
                **common_vals,
                "name": "TEST Import",
                "filepath": cls.directory_input,
                "avoid_duplicated_files": True,
            }
        )
        cls.task_delete = AST.create(
            {
                **common_vals,
                "name": "TEST Import then delete",
                "after_import": "delete",
                "filepath": cls.directory_input,
            }
        )
        cls.task_rename = AST.create(
            {
                **common_vals,
                "name": "TEST Import then rename",
                "after_import": "rename",
                "filepath": cls.directory_input,
                "new_name": "test-${obj.name}",
            }
        )
        cls.task_move = AST.create(
            {
                **common_vals,
                "name": "TEST Import then move",
                "after_import": "move",
                "filepath": cls.directory_input,
                "move_path": cls.directory_archived,
            }
        )
        cls.task_move_rename = AST.create(
            {
                **common_vals,
                "name": "TEST Import then move and rename",
                "after_import": "move_rename",
                "filepath": cls.directory_input,
                "move_path": cls.directory_archived,
                "new_name": "foo.txt",
            }
        )
        cls.task_export = AST.create(
            {
                "backend_id": cls.backend.id,
                "method_type": "export",
                "name": "TEST Export",
                "filepath": cls.directory_output,
            }
        )

    def setUp(self):
        super().setUp()
        self._clean_testing_directory()
        self._create_test_file()

    def tearDown(self):
        self._clean_testing_directory()
        super().tearDown()
