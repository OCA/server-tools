# Copyright - 2015-2018 Therp BV <https://acme.com>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase

from ..match_algorithm import email_domain, email_exact, odoo_standard

MSG_BODY = [
    (
        "1 (RFC822 {1149}",
        "Return-Path: <ronald@acme.com>\r\n"
        "Delivered-To: demo@yourcompany.example.com\r\n"
        "Received: from localhost (localhost [127.0.0.1])\r\n"
        "\tby vanaheim.acme.com (Postfix) with ESMTP id 14A3183163\r\n"
        "\tfor <demo@yourcompany.example.com>;"
        " Mon, 26 Mar 2018 16:03:52 +0200 (CEST)\r\n"
        "To: Test User <demo@yourcompany.example.com>\r\n"
        "From: Ronald Portier <ronald@acme.com>\r\n"
        "Subject: test\r\n"
        "Message-ID: <485a8041-d560-a981-5afc-d31c1f136748@acme.com>\r\n"
        "Date: Mon, 26 Mar 2018 16:03:51 +0200\r\n"
        "User-Agent: Mock Test\r\n"
        "MIME-Version: 1.0\r\n"
        "Content-Type: text/plain; charset=utf-8\r\n"
        "Content-Language: en-US\r\n"
        "Content-Transfer-Encoding: 7bit\r\n\r\n"
        "Hallo Wereld!\r\n",
    ),
    ")",
]


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
                "mail_field": "to,from",
            }
        )

    def do_matching(
        self,
        match_algorithm,
        expected_xmlid,
        folder,
        mail_message,
        mail_message_org=None,
    ):
        matcher = match_algorithm()
        matches = matcher.search_matches(folder, mail_message)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], self.env.ref(expected_xmlid))
        connection = MockConnection()
        matcher.handle_match(
            connection, matches[0], folder, mail_message, mail_message_org, None
        )

    def test_email_exact(self):
        mail_message = {
            "subject": "Testsubject",
            "to": "demo@yourcompany.example.com",
            "from": "someone@else.com",
        }
        folder = self.folder
        self.do_matching(
            email_exact.EmailExact, "base.user_demo_res_partner", folder, mail_message
        )
        self.assertEqual(
            self.env.ref("base.user_demo_res_partner").message_ids.subject,
            mail_message["subject"],
        )

    def test_email_domain(self):
        mail_message = {
            "subject": "Testsubject",
            "to": "test@seagate.com",
            "from": "someone@else.com",
            "attachments": [("hello.txt", "Hello World!")],
        }
        folder = self.folder
        folder.match_algorithm = "email_domain"
        folder.use_first_match = True
        self.do_matching(
            email_domain.EmailDomain,
            "base.res_partner_address_31",
            folder,
            mail_message,
        )
        self.assertEqual(
            self.env.ref("base.res_partner_address_31").message_ids.subject,
            mail_message["subject"],
        )

    def test_odoo_standard(self):
        mail_message_org = (
            "To: demo@yourcompany.example.com\n"
            "From: someone@else.com\n"
            "Subject: testsubject\n"
            "Message-Id: 42\n"
            "Hello world"
        )
        folder = self.folder
        folder.match_algorithm = "odoo_standard"
        matcher = odoo_standard.OdooStandard()
        matches = matcher.search_matches(folder, None)
        self.assertEqual(len(matches), 1)
        matcher.handle_match(None, matches[0], folder, None, mail_message_org, None)
        self.assertIn(
            "Hello world",
            self.env["mail.message"].search([("subject", "=", "testsubject")]).body,
        )

    def test_apply_matching_exact(self):
        folder = self.folder
        folder.match_algorithm = "email_domain"
        connection = MockConnection()
        msgid = "<485a8041-d560-a981-5afc-d31c1f136748@acme.com>"
        matcher = email_exact.EmailExact()
        folder.apply_matching(connection, msgid, matcher)

    def test_retrieve_imap_folder_domain(self):
        folder = self.folder
        folder.match_algorithm = "email_domain"
        connection = MockConnection()
        folder.retrieve_imap_folder(connection)
