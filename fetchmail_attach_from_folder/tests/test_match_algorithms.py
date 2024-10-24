# Copyright - 2015-2018 Therp BV <https://acme.com>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=method-required-super
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
        "Hallo Wereld!\r\n" % {"test_email": TEST_EMAIL, "test_subject": TEST_SUBJECT},
    )
]
MAIL_MESSAGE = {"subject": TEST_SUBJECT, "to": "demo@yourcompany.example.com"}


class MockConnection:
    def select(self, path):
        """Mock selecting a folder."""
        return ("OK",)

    def create(self, path):
        """Mock creating a folder."""
        return ("OK",)

    def store(self, message_uid, msg_item, value):
        """Mock store command."""
        return "OK"

    def copy(self, message_uid, folder_path):
        """Mock copy command."""
        return "OK"

    def fetch(self, message_uid, parts):
        """Return RFC822 formatted message."""
        return ("OK", MSG_BODY)

    def search(self, charset, criteria):
        """Return some message uid's."""
        return ("OK", ["123 456"])

    def uid(self, command, *args):
        """Return from the appropiate mocked method."""
        method = getattr(self, command)
        return method(*args)


class TestMatchAlgorithms(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner_model = cls.env["res.partner"]
        cls.test_partner = cls.partner_model.with_context(tracking_disable=True).create(
            {
                "name": "Reynaert de Vos",
                "email": TEST_EMAIL,
                "is_company": False,
                "category_id": [
                    (6, 0, []),
                ],
            }
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
        cls.partner_ir_model = cls.env["ir.model"].search(
            [
                ("model", "=", cls.partner_model._name),
            ],
            limit=1,
        )
        cls.partner_category = cls.env.ref("base.res_partner_category_12")
        cls.server_action = cls.env["ir.actions.server"].create(
            {
                "name": "Action Set Active Partner",
                "model_id": cls.partner_ir_model.id,
                "state": "object_write",
                "code": False,
                "fields_lines": [
                    (
                        0,
                        0,
                        {
                            "col1": cls.env["ir.model.fields"]
                            .search(
                                [
                                    ("name", "=", "category_id"),
                                    ("model_id", "=", cls.partner_ir_model.id),
                                ],
                                limit=1,
                            )
                            .id,
                            "evaluation_type": "equation",
                            "value": str([cls.partner_category.id]),
                        },
                    ),
                ],
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
        message_uid = "<485a8041-d560-a981-5afc-d31c1f136748@acme.com>"
        folder.apply_matching(connection, message_uid)

    def test_retrieve_imap_folder_domain(self):
        folder = self.folder
        folder.match_algorithm = "email_domain"
        connection = MockConnection()
        folder.retrieve_imap_folder(connection)

    def test_archive_messages(self):
        folder = self.folder
        folder.archive_path = "archived_messages"
        connection = MockConnection()
        folder.retrieve_imap_folder(connection)

    def test_non_action(self):
        connection = MockConnection()
        self.folder.action_id = False
        self.folder.apply_matching(connection, "1")
        self.assertFalse(self.test_partner.category_id)

    def test_action(self):
        connection = MockConnection()
        self.folder.action_id = self.server_action
        self.folder.apply_matching(connection, "1")
        self.assertEqual(self.partner_category, self.test_partner.category_id)
