# Copyright 2025 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import io

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.service import db
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestAutoBackupFsFile(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.DbBackup = cls.env["db.backup"]
        cls.DbBackupFsFile = cls.env["db.backup.fs.file"]
        cls.FsStorage = cls.env["fs.storage"]

        cls.env.ref("auto_backup_fs_file.fs_storage_auto_backup").unlink()

        # Create a test FS Storage
        cls.test_storage = cls.FsStorage.create(
            {
                "name": "Test Storage",
                "protocol": "memory",  # Use in-memory for testing
                "code": "mem_dir",
                "directory_path": "/tmp/",
            }
        )

    def setUp(self):
        super().setUp()
        # Patch db.dump_db to avoid actual DB dumping (active for the entire test)
        self.patch(
            db,
            "dump_db",
            lambda dbname, stream, backup_format: io.BytesIO(b"fake_backup_data"),
        )

    def _create_backup_config(self):
        # Create a test backup configuration with fs_file method
        return self.DbBackup.create(
            {
                "method": "fs_file",
                "backup_format": "zip",
                "days_to_keep": 7,
                "responsible_id": self.env.user.id,
            }
        )

    def _action_backup(self, backup_config):
        backup_config.action_backup()

    def test_ordinary_flow(self):
        """Test the ordinary flow of creating a backup configuration and performing
        backups."""
        # Create backup configuration, field not linked to storage yet
        with self.assertRaises(ValidationError):
            self._create_backup_config()

        self.test_storage.field_xmlids = (
            "auto_backup_fs_file.field_db_backup_fs_file__backup_file"
        )
        backup_config = self._create_backup_config()
        self.assertEqual(
            backup_config.name,
            f"Fs File Backup - {backup_config._get_fs_storage().name}",
        )
        self.assertFalse(backup_config.folder)

        # Test computation of fs_file_backup_count
        self.assertEqual(backup_config.fs_file_backup_count, 0)

        # Test backup generation and activity creation
        self._action_backup(
            backup_config
        )  # No need for _action_backup_with_time_freeze
        self.assertEqual(backup_config.fs_file_backup_count, 1)

        # Check activity scheduled
        activity = self.env["mail.activity"].search(
            [
                ("res_model", "=", "db.backup.fs.file"),
                ("res_id", "=", backup_config.fs_file_backup_ids.id),
                (
                    "activity_type_id",
                    "=",
                    self.env.ref("auto_backup_fs_file.mail_act_download_backup").id,
                ),
            ]
        )
        self.assertTrue(activity)
        self.assertEqual(activity.user_id, self.env.user)
        self.assertFalse(
            backup_config.fs_file_backup_ids.is_expired
        )  # Without active mock, not expired
        backup_config.cleanup()
        self.assertEqual(backup_config.fs_file_backup_count, 1)

        # Get the fs_backup for expiry testing
        fs_backup = backup_config.fs_file_backup_ids

        # Compute the expiration date
        computed_now = fields.Datetime.add(
            fs_backup.create_date, days=backup_config.days_to_keep, seconds=10
        )

        def fake_now():
            return computed_now

        # Use self.patch to mock ONLY Datetime.now() for the duration of the test
        self.patch(fields.Datetime, "now", fake_now)
        fs_backup.invalidate_recordset(["is_expired"])

        self.assertTrue(
            fs_backup.is_expired
        )  # Triggers _compute_is_expired with mocked now
        backup_config.cleanup()  # Will use the computed is_expired

        self.assertEqual(backup_config.fs_file_backup_count, 0)

        # Verify the backing ir.attachment is also removed (GC chain fires via unlink)
        attachment = self.env["ir.attachment"].search(
            [
                ("res_model", "=", "db.backup.fs.file"),
                ("res_field", "=", "backup_file"),
            ]
        )
        self.assertFalse(attachment)

    def test_action_backup_triggers_cleanup(self):
        """cleanup() must fire for fs_file records via action_backup(), not just
        when called directly. Regression test for the bug where action_backup()
        only passed local/sftp records to successful.cleanup(), making fs_file
        cleanup dead code in production."""
        self.test_storage.field_xmlids = (
            "auto_backup_fs_file.field_db_backup_fs_file__backup_file"
        )
        backup_config = self._create_backup_config()

        # Run first backup — creates record at create_date = now
        self._action_backup(backup_config)
        self.assertEqual(backup_config.fs_file_backup_count, 1)
        first_backup = backup_config.fs_file_backup_ids

        # Make the first backup expired by setting an old create_date directly
        # (avoids patching Datetime.now which doesn't control ORM create_date)
        old_date = fields.Datetime.add(
            fields.Datetime.now(), days=-backup_config.days_to_keep - 1
        )
        self.env.cr.execute(
            "UPDATE db_backup_fs_file SET create_date = %s WHERE id = %s",
            (old_date, first_backup.id),
        )
        first_backup.invalidate_recordset(["is_expired", "create_date"])
        self.assertTrue(first_backup.is_expired)

        # Run second backup via action_backup() — this is the PRODUCTION call path.
        # cleanup() must be triggered automatically for the expired first backup.
        self._action_backup(backup_config)

        # First backup must be gone (cleanup deleted it)
        self.assertFalse(
            first_backup.exists(),
            "Expired backup was not deleted by action_backup()",
        )
        # A new backup should have been created
        self.assertTrue(backup_config.fs_file_backup_ids)
