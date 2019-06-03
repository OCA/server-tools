# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from tempfile import gettempdir

from odoo.tests import common
from odoo.exceptions import UserError


class TestAutoBackupDownload(common.TransactionCase):

    def test_01_create_not_existing(self):
        backup_dir = self.env.ref(
            'auto_backup_download.default_backup_directory')

        # test method get_dir()
        with self.assertRaises(UserError):
            backup_dir.get_dir()

    def test_02_create_existing(self):
        backup_dir = self.env.ref(
            'auto_backup_download.default_backup_directory')
        self.env['db.backup'].create({
            'name': 'Test Backup 1',
            'folder': gettempdir()
        })

        # test method get_dir()
        full_dir = backup_dir.get_dir()
        self.assertEqual(full_dir[-1], '/')

        # test computed field file_ids
        self.assertGreaterEqual(len(backup_dir.file_ids), 0)

        # test count list of directory
        self.assertEqual(len(backup_dir.file_ids), backup_dir.file_count)

        # test reload list of directory
        backup_dir.reload()
        self.assertEqual(len(backup_dir.file_ids), backup_dir.file_count)
