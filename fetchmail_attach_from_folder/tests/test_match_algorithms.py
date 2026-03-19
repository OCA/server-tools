# Copyright - 2015-2026 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=method-required-super
from datetime import datetime
from unittest.mock import patch

from odoo import fields
from odoo.fields import Command
from odoo.tests.common import TransactionCase

from ..match_algorithm import email_domain
from .common import get_message_body

TEST_EMAIL = "reynaert@dutchsagas.nl"
TEST_SUBJECT = "Test subject"
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
        """Return RFC822 formatted message.

        By passing special values in message_uid, we can manipulate
        the body returned.
        """
        email = (
            "the_smart_red_one@reynaerde.waesland"
            if message_uid == "test no match"
            else TEST_EMAIL
        )
        return ("OK", get_message_body(email, TEST_SUBJECT))

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
        cls.PartnerCategory = cls.env["res.partner.category"]
        cls.partner_category = cls.PartnerCategory.create({"name": "Test Partners"})
        cls.Partner = cls.env["res.partner"]
        cls.test_partner = cls.Partner.with_context(tracking_disable=True).create(
            {
                "name": "Reynaert de Vos",
                "email": TEST_EMAIL,
                "is_company": False,
                "category_id": [Command.clear()],
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
                ("model", "=", cls.Partner._name),
            ],
            limit=1,
        )
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

    def test_apply_matching_exact_no_match(self):
        folder = self.folder
        folder.match_algorithm = "email_exact"
        connection = MockConnection()
        message_uid = "test no match"
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

    def test_get_criteria(self):
        self.folder.write({"fetch_unseen_only": False, "fetch_last_day_only": False})
        criteria = self.folder.get_criteria()
        self.assertEqual(criteria, "UNDELETED")
        self.folder.write({"fetch_unseen_only": True, "fetch_last_day_only": False})
        criteria = self.folder.get_criteria()
        self.assertEqual(criteria, "UNSEEN UNDELETED")
        self.folder.write({"fetch_last_day_only": True})
        criteria = self.folder.get_criteria()
        criteria_words = criteria.split()
        criteria_words[0] = "SINCE"
        since_date = datetime.strptime(criteria_words[1], "%d-%b-%Y").date()
        yesterday = fields.Date.subtract(fields.Date.context_today(self.folder), days=1)
        self.assertEqual(since_date, yesterday)

    def test_action(self):
        connection = MockConnection()
        self.folder.action_id = self.server_action
        self.folder.apply_matching(connection, "1")
        self.assertEqual(self.partner_category, self.test_partner.category_id)

    def test_button_confirm_folder(self):
        """Test the button_confirm_folder method."""
        folder = self.folder
        with patch.object(
            self.server.__class__, "_connect__", return_value=MockConnection()
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
