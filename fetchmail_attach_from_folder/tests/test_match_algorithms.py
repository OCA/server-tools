# Copyright - 2015-2018 Therp BV <https://acme.com>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase

from ..match_algorithm import email_domain

TEST_EMAIL = "reynaert@dutchsagas.nl"
TEST_SUBJECT = "Test subject"
MSG_BODY = [
    (
        "1 (RFC822 {1149}",
        "Return-Path: <ronald@acme.com>\r\n"
        "Delivered-To: demo@yourcompany.example.com\r\n"
        "Received: from localhost (localhost [127.0.0.1])\r\n"
        "\tby vanaheim.acme.com (Postfix) with ESMTP id 14A3183163\r\n"
        "\tfor <demo@yourcompany.example.com>;"
        " Mon, 26 Mar 2018 16:03:52 +0200 (CEST)\r\n"
        "To: Test User <nonexistingemail@yourcompany.example.com>\r\n"
        "From: Reynaert de Vos <%(test_email)s>\r\n"
        "Subject: %(test_subject)s\r\n"
        "Message-ID: <485a8041-d560-a981-5afc-d31c1f136748@acme.com>\r\n"
        "Date: Mon, 26 Mar 2018 16:03:51 +0200\r\n"
        "User-Agent: Mock Test\r\n"
        "MIME-Version: 1.0\r\n"
        "Content-Type: text/plain; charset=utf-8\r\n"
        "Content-Language: en-US\r\n"
        "Content-Transfer-Encoding: 7bit\r\n\r\n"
        "Hallo Wereld!\r\n"
        % {
            "test_email": TEST_EMAIL,
            "test_subject": TEST_SUBJECT,
        },
    ),
]
MAIL_MESSAGE = {
    "subject": TEST_SUBJECT,
    "to": "demo@yourcompany.example.com",
}


class MockConnection:
    def select(self, path):
        """Mock selecting a folder."""
        return ("OK",)

    def store(self, msgid, msg_item, value):
        """Mock store command."""
        return "OK"

    def fetch(self, msgid, parts):
        """Return RFC822 formatted message."""
        return ("OK", MSG_BODY)

    def search(self, charset, criteria):
        """Return some msgid's."""
        return ("OK", ["123 456"])


class TestMatchAlgorithms(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner_model = cls.env["res.partner"]
        cls.test_partner = cls.partner_model.with_context(tracking_disable=True).create(
            {"name": "Reynaert de Vos", "email": TEST_EMAIL, "is_company": False}
        )
        cls.server_model = cls.env["fetchmail.server"]
        cls.folder_model = cls.env["fetchmail.server.folder"]
        cls.server = cls.server_model.create(
            {
                "name": "Test Fetchmail Server",
                "server": "imap.example.com",
                "server_type": "imap",
                "active": True,
                "state": "done",
            }
        )
        cls.folder = cls.folder_model.create(
            {
                "server_id": cls.server.id,
                "sequence": 5,
                "path": "INBOX",
                "model_id": cls.env.ref("base.model_res_partner").id,
                "model_field": "email",
                "match_algorithm": "email_exact",
                # The intention is to link email to sender partner object.
                "mail_field": "from",
            }
        )

    def test_email_exact(self):
        """A message to ronald@acme.com should be linked to partner with that email."""
        MAIL_MESSAGE["from"] = TEST_EMAIL
        self._test_search_matches(email_domain.EmailDomain)
        self._test_apply_matching(email_domain.EmailDomain)

    def test_email_domain(self):
        """Test with email in same domain, but different mailbox."""
        ALTERNATE_EMAIL = TEST_EMAIL.replace("reynaert@", "mariken@")
        MAIL_MESSAGE["from"] = ALTERNATE_EMAIL
        self.folder.match_algorithm = "email_domain"
        self.folder.match_first = True
        self._test_search_matches(email_domain.EmailDomain)
        self._test_apply_matching(email_domain.EmailDomain)

    def _test_search_matches(self, match_algorithm):
        matcher = match_algorithm()
        matches = matcher.search_matches(self.folder, MAIL_MESSAGE)
        # matches should be a record set with length 1.
        self.assertEqual(matches.email, self.test_partner.email)
        self.assertEqual(matches, self.test_partner)

    def _test_apply_matching(self, match_algorithm):
        connection = MockConnection()
        thread_id = self.folder.apply_matching(connection, "1")
        self.assertEqual(thread_id, self.test_partner.id)
        self.assertEqual(self.test_partner.message_ids[-1].subject, TEST_SUBJECT)

    def test_apply_matching_exact(self):
        folder = self.folder
        folder.match_algorithm = "email_exact"
        connection = MockConnection()
        msgid = "<485a8041-d560-a981-5afc-d31c1f136748@acme.com>"
        folder.apply_matching(connection, msgid)

    def test_retrieve_imap_folder_domain(self):
        folder = self.folder
        folder.match_algorithm = "email_domain"
        connection = MockConnection()
        folder.retrieve_imap_folder(connection)
