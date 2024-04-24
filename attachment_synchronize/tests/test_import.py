# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from .common import SyncCommon


class TestImport(SyncCommon):
    def tearDown(self):
        self.registry.leave_test_mode()
        super().tearDown()

    def setUp(self):
        super().setUp()
        self.registry.enter_test_mode(self.env.cr)
        self.env = api.Environment(
            self.registry.test_cr, self.env.uid, self.env.context
        )

    @property
    def archived_files(self):
        return self.backend.fs.ls(self.directory_archived, detail=False)

    @property
    def input_files(self):
        return self.backend.fs.ls(self.directory_input, detail=False)

    def _check_attachment_created(self, count=1):
        with self.env.registry.cursor() as new_cr:
            attachment = self.env(cr=new_cr)["attachment.queue"].search(
                [("name", "=", "bar.txt")]
            )
            self.assertEqual(len(attachment), count)

    def test_import_with_rename(self):
        self.task_rename.run_import()
        self._check_attachment_created()
        self.assertEqual(self.input_files, ["test_import/test-bar.txt"])
        self.assertEqual(self.archived_files, [])

    def test_import_with_move(self):
        self.task_move.run_import()
        self._check_attachment_created()
        self.assertEqual(self.input_files, [])
        self.assertEqual(self.archived_files, ["test_archived/bar.txt"])

    def test_import_with_move_and_rename(self):
        self.task_move_rename.run_import()
        self._check_attachment_created()
        self.assertEqual(self.input_files, [])
        self.assertEqual(self.archived_files, ["test_archived/foo.txt"])

    def test_import_with_delete(self):
        self.task_delete.run_import()
        self._check_attachment_created()
        self.assertEqual(self.input_files, [])
        self.assertEqual(self.archived_files, [])

    def test_import_twice(self):
        self.task_delete.run_import()
        self._check_attachment_created(count=1)

        self._create_test_file()
        self.task_delete.run_import()
        self._check_attachment_created(count=2)

    def test_import_twice_no_duplicate(self):
        self.task.run_import()
        self._check_attachment_created(count=1)

        self._create_test_file()
        self.task.run_import()
        self._check_attachment_created(count=1)

    def test_running_cron(self):
        self.env["attachment.synchronize.task"].search(
            [("id", "!=", self.task.id)]
        ).write({"active": False})
        self.env["attachment.synchronize.task"].run_task_import_scheduler()
        self._check_attachment_created(count=1)

    def test_running_cron_disable_task(self):
        self.env["attachment.synchronize.task"].search([]).write({"active": False})
        self.env["attachment.synchronize.task"].run_task_import_scheduler()
        self._check_attachment_created(count=0)
