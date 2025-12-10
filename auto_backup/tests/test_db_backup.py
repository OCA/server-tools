# Copyright 2015 Agile Business Group <http://www.agilebg.com>
# Copyright 2015 Alessio Gerace <alesiso.gerace@agilebg.com>
# Copyright 2016 Grupo ESOC Ingenieria de Servicios, S.L.U. - Jairo Llopis
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import os
from contextlib import contextmanager
from datetime import datetime, timedelta
from unittest.mock import PropertyMock, patch

import pysftp
from paramiko import HostKeys

from odoo import tools
from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon

_logger = logging.getLogger(__name__)


model = "odoo.addons.auto_backup.models.db_backup"
class_name = "%s.DbBackup" % model


class TestConnectionException(pysftp.ConnectionException):
    def __init__(self):
        super().__init__("test", "test")


class TestDbBackup(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Model = cls.env["db.backup"]

    @contextmanager
    def mock_assets(self):
        """It provides mocked core assets"""
        self.path_join_val = "/this/is/a/path"
        with patch("%s.db" % model) as db:
            with patch("%s.os" % model) as os:
                with patch("%s.shutil" % model) as shutil:
                    os.path.join.return_value = self.path_join_val
                    yield {
                        "db": db,
                        "os": os,
                        "shutil": shutil,
                    }

    @contextmanager
    def patch_filtered_sftp(self, record):
        """It patches filtered record and provides a mock"""
        with patch("%s.filtered" % class_name) as filtered:
            filtered.side_effect = [], [record]
            with patch("%s.backup_log" % class_name):
                with patch("%s.sftp_connection" % class_name):
                    yield filtered

    def new_record(self, method="sftp", name_suffix=None):
        name = "Têst backup"
        if name_suffix is not None:
            name += f" {name_suffix}"
        elif self.env.registry.in_test_mode():  # always true in tests
            # make name unique per call
            name += f" {id(self)}-{datetime.now().microsecond}"
        vals = {
            "name": name,
            "method": method,
            "days_to_keep": 1,
        }
        if method == "sftp":
            vals.update(
                {
                    "sftp_host": "test_host",
                    "sftp_port": 222,
                    "sftp_user": "tuser",
                    "sftp_password": "password",
                    "folder": "/folder/",
                }
            )
        self.vals = vals
        return self.Model.create(vals)

    def test_compute_name_sftp(self):
        """It should create proper SFTP URI"""
        rec_id = self.new_record(name_suffix="compute_name_sftp")
        self.assertEqual(
            f"sftp://{self.vals['sftp_user']}@{self.vals['sftp_host']}:{self.vals['sftp_port']}{self.vals['folder']}",
            rec_id.name,
        )

    def test_check_folder(self):
        """It should not allow recursive backups"""
        rec_id = self.new_record("local", name_suffix="check_folder")
        with self.assertRaises(UserError):
            rec_id.write(
                {
                    "folder": "%s/another/path"
                    % tools.config.filestore(self.env.cr.dbname),
                }
            )

    @patch("%s._" % model)
    def test_action_sftp_test_connection_success(self, _):
        """It should raise connection succeeded warning"""
        with patch("%s.sftp_connection" % class_name, new_callable=PropertyMock):
            rec_id = self.new_record(name_suffix="test_connection_success")
            with self.assertRaises(UserError):
                rec_id.action_sftp_test_connection()
        _.assert_called_once_with("Connection Test Succeeded!")

    @patch("%s._" % model)
    def _test_action_sftp_test_connection_fail(self, _):
        """It should raise connection fail warning"""
        with patch(
            "%s.sftp_connection" % class_name, new_callable=PropertyMock
        ) as conn:
            rec_id = self.new_record(name_suffix="test_connection_fail")
            conn().side_effect = TestConnectionException
            with self.assertRaises(UserError):
                rec_id.action_sftp_test_connection()
            _.assert_called_once_with("Connection Test Failed!")

    def test_action_backup_local(self):
        """It should backup local database"""
        rec_id = self.new_record("local", name_suffix="backup_local")
        filename = rec_id.filename(datetime.now())
        rec_id.action_backup()
        generated_backup = [f for f in os.listdir(rec_id.folder) if f >= filename]
        self.assertEqual(1, len(generated_backup))

    def test_action_backup_local_cleanup(self):
        """Backup local database and cleanup old databases"""
        rec_id = self.new_record("local", name_suffix="backup_local_cleanup")
        old_date = datetime.now() - timedelta(days=3)
        filename = rec_id.filename(old_date)
        with patch("%s.datetime" % model) as mock_date:
            mock_date.now.return_value = old_date
            rec_id.action_backup()
        generated_backup = [f for f in os.listdir(rec_id.folder) if f >= filename]
        self.assertEqual(2, len(generated_backup))

        filename = rec_id.filename(datetime.now())
        rec_id.action_backup()
        generated_backup = [f for f in os.listdir(rec_id.folder) if f >= filename]
        self.assertEqual(1, len(generated_backup))

    def _test_action_backup_sftp_mkdirs(self):
        """It should create remote dirs"""
        rec_id = self.new_record(name_suffix="backup_sftp_mkdirs")
        with self.mock_assets():
            with self.patch_filtered_sftp(rec_id):
                with patch("%s.cleanup" % class_name, new_callable=PropertyMock):
                    conn = rec_id.sftp_connection()
                    rec_id.action_backup()
                    conn.makedirs.assert_called_once_with(rec_id.folder)

    def _test_action_backup_sftp_mkdirs_conn_exception(self):
        """It should guard from ConnectionException on remote.mkdirs"""
        rec_id = self.new_record(name_suffix="backup_sftp_mkdirs_conn_exception")
        with self.mock_assets():
            with self.patch_filtered_sftp(rec_id):
                with patch("%s.cleanup" % class_name, new_callable=PropertyMock):
                    conn = rec_id.sftp_connection()
                    conn.makedirs.side_effect = TestConnectionException
                    rec_id.action_backup()
                    # No error was raised, test pass
                    self.assertTrue(True)

    def test_action_backup_sftp_remote_open(self):
        """It should open remote file w/ proper args"""
        rec_id = self.new_record(name_suffix="backup_sftp_remote_open")
        with self.mock_assets() as assets:
            with patch("%s.cleanup" % class_name, new_callable=PropertyMock):
                with patch("%s.sftp_connection" % class_name) as mock_sftp_conn:
                    # Create a proper mock for the SFTP connection context manager
                    mock_remote = mock_sftp_conn.return_value.__enter__.return_value
                    rec_id.action_backup()
                    mock_remote.open.assert_called_once_with(
                        assets["os"].path.join(), "wb"
                    )

    def test_action_backup_all_search(self):
        """It should search all records"""
        rec_id = self.new_record(name_suffix="backup_action_backup_all_search")
        with patch("%s.search" % class_name, new_callable=PropertyMock):
            rec_id.action_backup_all()
            rec_id.search.assert_called_once_with([])

    def test_action_backup_all_return(self):
        """It should return result of backup operation"""
        rec_id = self.new_record(name_suffix="backup_action_backup_all_return")
        with patch("%s.search" % class_name, new_callable=PropertyMock):
            res = rec_id.action_backup_all()
            self.assertEqual(rec_id.search().action_backup(), res)

    @patch("%s.pysftp" % model)
    def test_sftp_connection(self, pysftp):
        """It should create the SFTP connection with correct arguments and cnopts"""

        # 1. Password authentication
        rec_pwd = self.new_record(name_suffix="pwd")  # <-- unique name
        rec_pwd.sftp_connection()
        pysftp.Connection.assert_called_with(
            host=rec_pwd.sftp_host,
            username=rec_pwd.sftp_user,
            port=rec_pwd.sftp_port,
            password=rec_pwd.sftp_password,
            cnopts=pysftp.CnOpts.return_value,
        )

        # 2. Private key authentication
        pysftp.reset_mock()
        rec_key = self.new_record(name_suffix="key")  # <-- unique name
        rec_key.write({"sftp_private_key": "/fake/key", "sftp_password": "keypass"})
        rec_key.sftp_connection()
        pysftp.Connection.assert_called_with(
            host=rec_key.sftp_host,
            username=rec_key.sftp_user,
            port=rec_key.sftp_port,
            private_key=rec_key.sftp_private_key,
            private_key_pass=rec_key.sftp_password,
            cnopts=pysftp.CnOpts.return_value,
        )

    @patch("%s.pysftp" % model)
    def test_sftp_connection_return(self, pysftp):
        """It should return new sftp connection"""
        rec_id = self.new_record(name_suffix="return")
        res = rec_id.sftp_connection()
        self.assertEqual(
            pysftp.Connection(),
            res,
        )

    def test_filename_default(self):
        """It should not error and should return a .dump.zip file str"""
        now = datetime.now()
        res = self.Model.filename(now)
        self.assertTrue(res.endswith(".dump.zip"))

    def test_filename_zip(self):
        """It should return a dump.zip filenam"""
        now = datetime.now()
        res = self.Model.filename(now, ext="zip")
        self.assertTrue(res.endswith(".dump.zip"))

    def test_filename_dump(self):
        """It should return a dump filenam"""
        now = datetime.now()
        res = self.Model.filename(now, ext="dump")
        self.assertTrue(res.endswith(".dump"))

    def test_sftp_host_key_verification(self):
        """Test all host public key scenarios: valid, invalid, and disabled"""
        backup = self.new_record(name_suffix="hostkey")

        # ------------------------------------------------------------------
        # 1. Valid key → HostKeys populated correctly, connection created
        # ------------------------------------------------------------------
        with patch("pysftp.Connection") as mock_conn:
            backup.host_public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCqGKukO1De7zhZj6+H0qtjTkVxwTCpvKe4eCZ0FPqri0cb2JZfXJ/DgYSF6vUpwmJG8wVQZKjeGcjDOL5UlsuusFncCzWBQ7RKNUSesmQRMSGkVb1/3j+skZ6UtW+5u09lHNsj6tQ51s1SPrCBkedbNf0Tp0GbMJDyR4e9T04ZZwIDAQAB"  # noqa: E501
            backup.sftp_connection()  # Parses real key, no exception

            # Verify cnopts.hostkeys has the entry for our host
            cnopts = mock_conn.call_args.kwargs["cnopts"]
            self.assertIsInstance(cnopts.hostkeys, HostKeys)
            self.assertIn(backup.sftp_host, cnopts.hostkeys)
            keys = cnopts.hostkeys.lookup(backup.sftp_host)
            self.assertIsNotNone(keys)
            self.assertEqual(len(keys), 1)

        # ------------------------------------------------------------------
        # 2. Invalid format (too few parts) → "Invalid host public key"
        # ------------------------------------------------------------------
        backup.host_public_key = "invalid"  # len(parts) < 2 → ValueError
        with self.assertRaises(UserError) as cm:
            backup.sftp_connection()
        self.assertIn("Invalid host public key", str(cm.exception))

        # ------------------------------------------------------------------
        # 3. Valid format but bad base64 (padding error) →
        # "Error loading host public key"
        # ------------------------------------------------------------------
        backup.host_public_key = "ssh-rsa ABC"  # decodebytes() fails → binascii.Error
        with self.assertRaises(UserError) as cm:
            backup.sftp_connection()
        self.assertIn("Error loading host public key", str(cm.exception))

        # ------------------------------------------------------------------
        # 4. Empty key → cnopts.hostkeys = None (backward compatible, no warning)
        # ------------------------------------------------------------------
        with patch("pysftp.Connection") as mock_conn:
            backup.host_public_key = None
            backup.sftp_connection()
