# Copyright 2025 Binhex
# License AGPL-3.0 or later[](https://www.gnu.org/licenses/agpl).

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
