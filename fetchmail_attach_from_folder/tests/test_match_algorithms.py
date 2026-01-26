# Copyright - 2015-2018 Therp BV <https://acme.com>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=method-required-super
from unittest.mock import MagicMock, patch

from odoo.tests.common import TransactionCase

from odoo.addons.mail.models.fetchmail import FetchmailServer

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
        f"From: Reynaert de Vos <{TEST_EMAIL}>\r\n"
        f"Subject: {TEST_SUBJECT}\r\n"
        "Message-ID: <485a8041-d560-a981-5afc-d31c1f136748@acme.com>\r\n"
        "Date: Mon, 26 Mar 2018 16:03:51 +0200\r\n"
        "User-Agent: Mock Test\r\n"
        "MIME-Version: 1.0\r\n"
        "Content-Type: text/plain; charset=utf-8\r\n"
        "Content-Language: en-US\r\n"
        "Content-Transfer-Encoding: 7bit\r\n\r\n"
        "Hallo Wereld!\r\n",
    )
]
MAIL_MESSAGE = {"subject": TEST_SUBJECT, "to": "demo@yourcompany.example.com"}


class MockConnection:
    def select(self, path=None):
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

    def close(self):
        pass

    def expunge(self):
        """Mock an IMAP4.expunge action"""
        return ("OK", None)

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
                "state": "object_write",
                "update_path": "category_id",
                "evaluation_type": "value",
                "value": str(cls.partner_category.id),
                "model_id": cls.partner_ir_model.id,
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

    def test_button_confirm_folder(self):
        """Test the button_confirm_folder method."""
        folder = self.folder
        with patch.object(
            self.server.__class__, "connect", return_value=MockConnection()
        ):
            folder.active = False
            folder.button_confirm_folder()
            self.assertEqual(folder.state, "draft")

            folder.active = True
            folder.button_confirm_folder()
            self.assertEqual(folder.state, "done")

    def test_set_draft(self):
        """Test the set_draft method."""
        folder = self.folder
        res = folder.set_draft()
        self.assertEqual(res, True)
        self.assertEqual(folder.state, "draft")


class TestAttachMailManually(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Wizard = cls.env["fetchmail.attach.mail.manually"]
        cls.Folder = cls.env["fetchmail.server.folder"]
        cls.Partner = cls.env["res.partner"]

        cls.server = cls.env["fetchmail.server"].create(
            {
                "name": "Test IMAP",
                "server": "imap.example.com",
                "server_type": "imap",
                "user": "test@example.com",
                "password": "secret",
                "state": "done",
            }
        )

        cls.folder = cls.Folder.create(
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

        cls.partner = cls.Partner.create(
            {"name": "Test Partner", "email": "test@example.com"}
        )

    def _mock_connection(self):
        mock_conn = MagicMock()
        mock_conn.select.return_value = ("OK",)
        mock_conn.search.return_value = ("OK", [b"1"])
        mock_conn.uid.return_value = ("OK", [b"1"])
        mock_conn.fetch.return_value = (
            "OK",
            [(b"1 (RFC822 {123}", b"Mocked raw email content")],
        )
        mock_conn.list.return_value = (
            "OK",
            [b'(\\HasNoChildren) "." "INBOX"', b'(\\HasChildren) "." "Sent"'],
        )
        return mock_conn

    def _mock_fetch_msg(self, connection, message_uid):
        """Return a tuple like the real fetch_msg: (dict, bytes)"""
        mail_message = {
            "subject": "Test",
            "date": "2025-07-23 12:00:00",
            "from": "test@example.com",
            "body": "<p>Body</p>",
        }
        raw_message = b"Raw MIME message here"
        return mail_message, raw_message

    @patch.object(FetchmailServer, "connect")
    def test_default_get_populates_mail_ids(self, mock_connect):
        """Test that default_get loads emails into wizard."""
        mock_conn = self._mock_connection()
        mock_connect.return_value = mock_conn

        with (
            patch.object(
                self.folder.__class__, "fetch_msg", side_effect=self._mock_fetch_msg
            ),
            patch.object(
                self.folder.__class__, "get_message_uids", return_value=[b"1"]
            ),
            patch.object(self.folder.__class__, "get_criteria", return_value="ALL"),
        ):
            wizard = self.Wizard.with_context(folder_id=self.folder.id).create({})
            self.assertEqual(len(wizard.mail_ids), 1)
            self.assertEqual(wizard.mail_ids[0].subject, "Test")

    @patch.object(FetchmailServer, "connect")
    def test_attach_mails_only_with_object_id(self, mock_connect):
        """Only mails with object_id should be attached."""
        mock_conn = self._mock_connection()
        mock_connect.return_value = mock_conn
        with patch.object(
            self.folder.__class__,
            "fetch_msg",
            side_effect=lambda conn, message_uid: (
                {
                    "subject": "With Object",
                    "date": "2025-07-23",
                    "from": "test@example.com",
                    "body": "<p>Body</p>",
                },
                b"raw_message",
            ),
        ):
            wizard = self.Wizard.create(
                {
                    "folder_id": self.folder.id,
                    "mail_ids": [
                        (
                            0,
                            0,
                            {
                                "message_uid": "1",
                                "subject": "No Object",
                                "object_id": False,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "message_uid": "2",
                                "subject": "With Object",
                                "object_id": f"res.partner,{self.partner.id}",
                            },
                        ),
                    ],
                }
            )
            with patch.object(self.folder.__class__, "attach_mail") as mock_attach:
                with patch.object(self.folder.__class__, "update_msg"):
                    wizard.attach_mails()
                    mock_attach.assert_called_once()
                    args, _ = mock_attach.call_args
                    self.assertEqual(args[0], self.partner)

    def test_prepare_mail_returns_expected_dict(self):
        """Test _prepare_mail returns correct structure."""
        folder = self.folder
        message_uid = "123"
        mail_message = {
            "subject": "Test",
            "date": "2025-07-23",
            "from": "test@example.com",
            "body": "<p>Body</p>",
        }

        result = self.Wizard._prepare_mail(folder, message_uid, mail_message)
        expected = {
            "message_uid": "123",
            "subject": "Test",
            "date": "2025-07-23",
            "body": "<p>Body</p>",
            "email_from": "test@example.com",
            "object_id": "res.partner,-1",
        }
        self.assertEqual(result, expected)

    def test_wizard_name_is_translated(self):
        """Test that default name is translated."""
        with (
            patch.object(FetchmailServer, "connect", return_value=MagicMock()),
            patch.object(self.folder.__class__, "fetch_msg", return_value=({}, b"raw")),
            patch.object(
                self.folder.__class__, "get_message_uids", return_value=[b"1"]
            ),
            patch.object(self.folder.__class__, "get_criteria", return_value="ALL"),
        ):
            wizard = self.Wizard.with_context(folder_id=self.folder.id).create({})
            self.assertEqual(wizard.name, "Attach emails manually")

    def test_compute_folders_available_success(self):
        """Debe devolver las carpetas disponibles."""
        with patch.object(
            self.server.__class__, "connect", return_value=self._mock_connection()
        ):
            result = self.server.folders_available
            self.assertEqual(result, "INBOX\nSent")

    def test_compute_folders_available_not_done(self):
        """Si el servidor no está confirmado, debe advertir."""
        self.server.state = "draft"
        result = self.server.folders_available
        self.assertEqual(result, "Confirm connection first.")

    def test_compute_folders_available_list_error(self):
        """Si list() falla, debe mostrar mensaje de error."""
        mock_conn = MagicMock()
        mock_conn.list.return_value = ("NO", [])
        with patch.object(self.server.__class__, "connect", return_value=mock_conn):
            result = self.server.folders_available
            self.assertEqual(result, "Unable to retrieve folders.")
