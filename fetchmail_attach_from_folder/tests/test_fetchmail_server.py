# Copyright - 2013-2024 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from unittest.mock import patch

from odoo.tests.common import TransactionCase


class TestFetchmailServer(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.server = cls.env["fetchmail.server"].create(
            {
                "name": "Test Server",
                "server": "imap.example.com",
                "server_type": "imap",
                "user": "test@example.com",
                "password": "secret",
                "state": "done",
                "folders_only": False,
            }
        )

    def test_fetch_mails_accepts_raise_exception_argument(self):
        with patch.object(
            self.server.__class__,
            "connect",
            side_effect=AssertionError("Connection should not be attempted"),
        ):
            result = self.server.fetch_mail(raise_exception=False)

        self.assertTrue(result)
