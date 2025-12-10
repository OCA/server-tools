# Copyright 2015 Agile Business Group <http://www.agilebg.com>
# Copyright 2015 Alessio Gerace <alesiso.gerace@agilebg.com>
# Copyright 2016 Grupo ESOC Ingenieria de Servicios, S.L.U. - Jairo Llopis
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import os
import shutil
import tempfile
from datetime import datetime, timedelta
from unittest.mock import ANY, patch

import pysftp
from paramiko import HostKeys

from odoo import tools
from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon

model = "odoo.addons.auto_backup.models.db_backup"

VALID_RSA_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCnBpnDfzzp0KqEGPjBvxLlfKZLTgS2hYrawc1CeEeALQs0jAjCYbPBs1IC8lpDWeIjNAIssTm4BBoT+X03bYjfcQRVAasI15X6xybKXLau9C+qnzNk90BCFVNCnJBh4lleJoLB+0X8Khis9T4QGcGDdDMpjZwvsGkobOY+Moc4qhTSh1OH+EHbARP0MWDxdF2MaJmYXmTbPOSZLteRuX/gG7gOzu04QsUH5HOwILwR7bxyaILpe7LnVICAa3sHS61FgXERw8V1mXOKytXP7ziXoTdvFupiWzOGWftbPUr30XAR+MzWlp/pRb1nUKen8XZ9gIkRk7WHt7UxL1hPYmsH"  # noqa: E501
VALID_ECDSA_KEY = "ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBGgW7LHl4HpI1QXORb6Z1CMTCBndGWBCCNDURjVVwhcY0NF517wBtFKkkeAArfKI4kDCyZOyqpWEE54GOLcIyok="  # noqa: E501


class TestDbBackup(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Model = cls.env["db.backup"]

    def setUp(self):
        super().setUp()
        self._record_counter = 0

    def new_record(self, method="sftp", name_suffix=None):
        """Return a backup configuration with a folder unique to this call.

        ``name`` is a stored computed field without an inverse, so it cannot be
        used to tell configurations apart: the compute overwrites it and two
        records sharing folder, method and credentials would collide on the
        ``UNIQUE(name)`` constraint. Uniqueness therefore comes from ``folder``.

        SFTP records pin ``VALID_RSA_KEY`` so that no test depends on the
        ``known_hosts`` file of the machine running the suite.
        """
        self._record_counter += 1
        suffix = name_suffix or "record_%d" % self._record_counter
        vals = {
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
                    "sftp_host_keys": VALID_RSA_KEY,
                    "folder": "/folder_%s/" % suffix,
                }
            )
        else:
            folder = os.path.join(
                tools.config["data_dir"], "backups", self.env.cr.dbname, suffix
            )
            self.addCleanup(shutil.rmtree, folder, ignore_errors=True)
            vals["folder"] = folder
        self.vals = vals
        return self.Model.create(vals)

    def _assert_pinned_rsa_key(self, cnopts, host):
        """Assert ``cnopts`` trusts exactly ``VALID_RSA_KEY`` for ``host``."""
        self.assertIsInstance(cnopts, pysftp.CnOpts)
        self.assertIsInstance(cnopts.hostkeys, HostKeys)
        keys = cnopts.hostkeys.lookup(host)
        self.assertIsNotNone(keys)
        self.assertEqual({"ssh-rsa"}, set(keys))
        self.assertEqual(
            VALID_RSA_KEY.split()[1].rstrip("="),
            keys["ssh-rsa"].get_base64().rstrip("="),
        )

    def _cnopts(self, **values):
        """Return the connection options of a record with ``values`` written."""
        rec = self.new_record()
        rec.write(values)
        return rec._get_sftp_cnopts()

    def test_compute_name_sftp(self):
        """It should create proper SFTP URI"""
        rec_id = self.new_record(name_suffix="compute_name_sftp")
        self.assertEqual(
            f"sftp://{self.vals['sftp_user']}@{self.vals['sftp_host']}:"
            f"{self.vals['sftp_port']}{self.vals['folder']}",
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

    def test_action_sftp_test_connection(self):
        """It should report the connection test result, success or failure"""
        rec = self.new_record(name_suffix="test_connection")
        with self.subTest("success"), patch.object(type(rec), "sftp_connection"):
            with self.assertRaisesRegex(UserError, "Connection Test Succeeded!"):
                rec.action_sftp_test_connection()
        error = pysftp.ConnectionException("host", "message")
        with self.subTest("failure"), patch.object(
            type(rec), "sftp_connection", side_effect=error
        ), self.assertRaisesRegex(UserError, "Connection Test Failed"):
            rec.action_sftp_test_connection()

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
        old_filename = rec_id.filename(old_date)

        with patch("%s.datetime" % model) as mock_date:
            mock_date.now.return_value = old_date
            rec_id.action_backup()
        self.assertEqual([old_filename], os.listdir(rec_id.folder))

        rec_id.action_backup()
        files = os.listdir(rec_id.folder)
        self.assertNotIn(old_filename, files)
        self.assertEqual(1, len(files))
        self.assertTrue(files[0].endswith(".dump.zip"))

    def test_action_backup_sftp_upload(self):
        """It should create the remote folder and open the file for writing"""
        rec = self.new_record(name_suffix="action_backup_sftp_upload")
        with patch("%s.db" % model) as db:
            with patch("%s.pysftp.Connection" % model) as connection:
                with patch.object(type(rec), "cleanup") as cleanup:
                    # Empty read ends shutil.copyfileobj right away
                    db.dump_db.return_value.read.return_value = b""
                    rec.action_backup()
        remote = connection.return_value.__enter__.return_value
        remote.makedirs.assert_called_once_with(rec.folder)
        path, mode = remote.open.call_args.args
        self.assertEqual("wb", mode)
        self.assertEqual(
            os.path.normpath(rec.folder), os.path.normpath(os.path.dirname(path))
        )
        self.assertTrue(os.path.basename(path).endswith(".dump.zip"))
        cleanup.assert_called_once_with()

    def test_action_backup_sftp_makedirs_connection_exception(self):
        """It should log and keep uploading when makedirs fails"""
        rec_id = self.new_record(name_suffix="action_backup_sftp_makedirs_exception")
        with patch("%s.db" % model) as db:
            with patch("%s.pysftp.Connection" % model) as connection:
                with patch.object(type(rec_id), "cleanup"):
                    db.dump_db.return_value.read.return_value = b""
                    remote = connection.return_value.__enter__.return_value
                    remote.makedirs.side_effect = pysftp.ConnectionException(
                        "host", "message"
                    )
                    with self.assertLogs(model, level="ERROR"):
                        rec_id.action_backup()
        remote.makedirs.assert_called_once_with(rec_id.folder)
        remote.open.assert_called_once()

    def test_action_backup_all(self):
        """It should back up every configuration and return the result"""
        rec = self.new_record("local", name_suffix="action_backup_all")
        result = object()
        with patch.object(type(rec), "search", return_value=rec) as search:
            with patch.object(
                type(rec), "action_backup", return_value=result
            ) as action_backup:
                self.assertIs(result, rec.action_backup_all())
        search.assert_called_once_with([])
        action_backup.assert_called_once_with()

    def test_sftp_connection(self):
        """It should connect with either credentials and the pinned key"""
        rec = self.new_record(name_suffix="sftp_connection")
        cases = [
            ("password", {}, {"password": rec.sftp_password}),
            (
                "private key",
                {"sftp_private_key": "/fake/key", "sftp_password": "keypass"},
                {"private_key": "/fake/key", "private_key_pass": "keypass"},
            ),
        ]
        for name, values, expected in cases:
            with self.subTest(name), patch("%s.pysftp.Connection" % model) as conn:
                rec.write(values)
                result = rec.sftp_connection()
            self.assertIs(conn.return_value, result)
            conn.assert_called_once_with(
                host=rec.sftp_host,
                username=rec.sftp_user,
                port=rec.sftp_port,
                **expected,
                cnopts=ANY,
            )
            self._assert_pinned_rsa_key(conn.call_args.kwargs["cnopts"], rec.sftp_host)

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

    def test_sftp_cnopts_no_key_and_no_known_hosts(self):
        """It should tell the user how to obtain a host key when there is none"""
        rec_id = self.new_record(name_suffix="cnopts_no_key")
        rec_id.sftp_host_keys = ""
        with patch(
            "%s.pysftp.known_hosts" % model, return_value="/nonexistent/known_hosts"
        ), self.assertRaises(UserError) as error:
            rec_id._get_sftp_cnopts()
        message = str(error.exception)
        self.assertIn("No host key available", message)
        self.assertIn("ssh-keyscan", message)
        self.assertIn(rec_id.sftp_host, message)

    def test_sftp_cnopts_known_hosts_fallback(self):
        """It should load the local known_hosts when no key is pinned"""
        rec_id = self.new_record(name_suffix="cnopts_known_hosts")
        rec_id.sftp_host_keys = ""
        with tempfile.NamedTemporaryFile(
            "w", suffix="_known_hosts", delete=False
        ) as handle:
            handle.write(f"{rec_id.sftp_host} {VALID_RSA_KEY}\n")
            known_hosts = handle.name
        self.addCleanup(os.unlink, known_hosts)
        with patch("%s.pysftp.known_hosts" % model, return_value=known_hosts):
            cnopts = rec_id._get_sftp_cnopts()
        self._assert_pinned_rsa_key(cnopts, rec_id.sftp_host)

    def test_sftp_cnopts_pinned_keys(self):
        """It should enforce the given keys and never read known_hosts"""
        cases = [
            ("bare key", VALID_RSA_KEY, {"ssh-rsa"}),
            (
                "keyscan line",
                "sftp.example.com %s user@example.com" % VALID_RSA_KEY,
                {"ssh-rsa"},
            ),
            (
                "several keys",
                f"{VALID_RSA_KEY}\n{VALID_ECDSA_KEY}",
                {"ssh-rsa", "ecdsa-sha2-nistp256"},
            ),
        ]
        for name, keys, expected in cases:
            with self.subTest(name), patch(
                "%s.pysftp.known_hosts" % model,
                side_effect=AssertionError("known_hosts must not be read"),
            ):
                cnopts = self._cnopts(sftp_host_keys=keys)
                self.assertEqual(expected, set(cnopts.hostkeys.lookup("test_host")))
                self.assertIsNone(cnopts.hostkeys.lookup("sftp.example.com"))

    def test_sftp_cnopts_invalid_keys(self):
        """It should reject unusable keys, pointing at the line"""
        cases = [
            ("no key type", "not-a-key", "Invalid host key on line 1"),
            (
                "bad base64",
                "host ssh-ed25519 not-base64",
                "Invalid host key on line 1",
            ),
            (
                "unsupported type",
                "ssh-unknown %s" % VALID_RSA_KEY.split()[1],
                "Unsupported host key on line 1",
            ),
        ]
        for name, keys, message in cases:
            with self.subTest(name), self.assertRaisesRegex(UserError, message):
                self._cnopts(sftp_host_keys=keys)

    def test_sftp_cnopts_ignore_hostkey(self):
        """It should disable host key checking on demand and warn about it"""
        rec_id = self.new_record(name_suffix="cnopts_ignore_hostkey")
        rec_id.sftp_ignore_hostkey = True
        with self.assertLogs(model, level="WARNING") as logs:
            cnopts = rec_id._get_sftp_cnopts()
        self.assertIsNone(cnopts.hostkeys)
        self.assertIn(
            "Host key verification disabled for the SFTP server %s" % rec_id.sftp_host,
            "\n".join(logs.output),
        )

    def test_cleanup_sftp_uses_pinned_key(self):
        """It should remove only expired remote backups, over a verified link"""
        rec_id = self.new_record(name_suffix="cleanup_sftp_pinned_key")
        old_name = "2000_01_01_00_00_00.dump.zip"
        current_name = rec_id.filename(datetime.now())
        with patch("%s.pysftp.Connection" % model) as connection:
            remote = connection.return_value.__enter__.return_value
            remote.listdir.return_value = [old_name, current_name, "notes.txt"]
            rec_id.cleanup()
        remote.listdir.assert_called_once_with(rec_id.folder)
        remote.unlink.assert_called_once_with(f"{rec_id.folder}/{old_name}")
        self._assert_pinned_rsa_key(
            connection.call_args.kwargs["cnopts"], rec_id.sftp_host
        )
