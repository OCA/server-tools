# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import SyncCommon


class TestImport(SyncCommon):
    @property
    def archived_files(self):
        return self.backend._list(self.directory_archived)

    @property
    def input_files(self):
        return self.backend._list(self.directory_input)

    def _check_attachment_created(self, count=1):
        attachment = self.env["attachment.queue"].search([("name", "=", "bar.txt")])
        self.assertEqual(len(attachment), count)

    def test_import_with_rename(self):
        self.task.write({"after_import": "rename", "new_name": "foo.txt"})
        self.task.run_import()
        self._check_attachment_created()
        self.assertEqual(self.input_files, ["foo.txt"])
        self.assertEqual(self.archived_files, [])

    def test_import_with_move(self):
        self.task.write({"after_import": "move", "move_path": self.directory_archived})
        self.task.run_import()
        self._check_attachment_created()
        self.assertEqual(self.input_files, [])
        self.assertEqual(self.archived_files, ["bar.txt"])

    def test_import_with_move_and_rename(self):
        self.task.write(
            {
                "after_import": "move_rename",
                "new_name": "foo.txt",
                "move_path": self.directory_archived,
            }
        )
        self.task.run_import()
        self._check_attachment_created()
        self.assertEqual(self.input_files, [])
        self.assertEqual(self.archived_files, ["foo.txt"])

    def test_import_with_delete(self):
        self.task.write({"after_import": "delete"})
        self.task.run_import()
        self._check_attachment_created()
        self.assertEqual(self.input_files, [])
        self.assertEqual(self.archived_files, [])

    def test_import_twice(self):
        self.task.write({"after_import": "delete"})
        self.task.run_import()
        self._check_attachment_created(count=1)

        self._create_test_file()
        self.task.run_import()
        self._check_attachment_created(count=2)

    def test_import_twice_no_duplicate(self):
        self.task.write({"after_import": "delete", "avoid_duplicated_files": True})
        self.task.run_import()
        self._check_attachment_created(count=1)

        self._create_test_file()
        self.task.run_import()
        self._check_attachment_created(count=1)

    def test_running_cron(self):
        self.task.write({"after_import": "delete"})
        self.env["attachment.synchronize.task"].run_task_import_scheduler()
        self._check_attachment_created(count=1)

    def test_running_cron_disable_task(self):
        self.task.write({"after_import": "delete", "active": False})
        self.env["attachment.synchronize.task"].run_task_import_scheduler()
        self._check_attachment_created(count=0)
