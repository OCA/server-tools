# Copyright 2017-20 ForgeFlow S.L. (www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import tagged

from odoo.addons.test_mail.data.test_mail_data import MAIL_TEMPLATE
from odoo.addons.test_mail.tests.test_mail_gateway import TestMailgateway


@tagged("mail_gateway")
class TestFetchmailIncomingLog(TestMailgateway):
    @classmethod
    def setUpClass(cls):
        super(TestFetchmailIncomingLog, cls).setUpClass()

        cls.fetchmail_server = cls.env["fetchmail.server"].create(
            {"name": "Test Fetchmail Server", "server_type": "imap"}
        )

    def test_message_process(self):
        email_from = "test1@example.com"
        to_email = "test2@example.com"
        msg_id = "Test log message to process"
        with self.assertRaises(ValueError):
            mail = MAIL_TEMPLATE.format(
                to=to_email,
                email_from=email_from,
                cc="",
                subject="testing",
                extra="",
                msg_id=msg_id,
                return_path="",
            )
            self.env["mail.thread"].with_context(
                fetchmail_server_id=self.fetchmail_server.id
            ).message_process(None, mail)
