from unittest.mock import MagicMock, patch

from odoo import fields

from odoo.addons.base.tests.common import BaseCommon


class TestMailCleanup(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.server = cls.env["fetchmail.server"].create(
            {
                "name": "Test",
                "server_type": "imap",
                "cleanup_days": 30,
                "cleanup_folder": "Archive",
                "purge_days": 90,
            }
        )

    def test_fields_declared(self):
        f = self.env["fetchmail.server"]._fields
        self.assertIsInstance(f["cleanup_days"], fields.Integer)
        self.assertIsInstance(f["cleanup_folder"], fields.Char)
        self.assertIsInstance(f["purge_days"], fields.Integer)

    def test_server_env_fields(self):
        keys = set(self.server._server_env_fields)
        self.assertTrue({"cleanup_days", "cleanup_folder", "purge_days"} <= keys)

    def test_cleanup_marks_seen_and_moves(self):
        imap = MagicMock()
        imap.search.return_value = ("OK", [b"1 2"])
        imap.copy.return_value = ("OK", None)
        self.server._cleanup_fetchmail_server(self.server, imap)
        flag_calls = [c.args for c in imap.store.call_args_list]
        self.assertIn((b"1", "+FLAGS", "\\Seen"), flag_calls)
        self.assertIn((b"2", "+FLAGS", "\\Seen"), flag_calls)
        self.assertEqual(imap.copy.call_count, 2)
        self.assertIn((b"1", "+FLAGS", "\\Deleted"), flag_calls)

    def test_purge_deletes_old_mail(self):
        imap = MagicMock()
        imap.search.return_value = ("OK", [b"5"])
        self.server._purge_fetchmail_server(self.server, imap)
        imap.store.assert_called_with(b"5", "+FLAGS", "\\Deleted")

    def test_cleanup_no_folder_only_marks_seen(self):
        self.server.cleanup_folder = False
        imap = MagicMock()
        imap.search.return_value = ("OK", [b"7"])
        self.server._cleanup_fetchmail_server(self.server, imap)
        imap.copy.assert_not_called()

    def test_fetch_mail_runs_cleanup_and_purge_on_imap(self):
        imap = MagicMock()
        imap.search.return_value = ("OK", [b""])
        with (
            patch.object(type(self.server), "_connect__", return_value=imap),
            patch(
                "odoo.addons.mail.models.fetchmail.FetchmailServer._fetch_mail",
                return_value=None,
            ),
        ):
            self.server._fetch_mail()
        imap.select.assert_called_once()
        imap.expunge.assert_called_once()
        imap.close.assert_called_once()
        imap.logout.assert_called_once()

    def test_fetch_mail_skipped_on_pop_server(self):
        self.server.server_type = "pop"
        with (
            patch.object(type(self.server), "_connect__") as mock_connect,
            patch(
                "odoo.addons.mail.models.fetchmail.FetchmailServer._fetch_mail",
                return_value=None,
            ),
        ):
            self.server._fetch_mail()
        mock_connect.assert_not_called()
