# Copyright 2021 Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# noqa: B902

import email
import threading

from odoo.tests.common import TransactionCase


class TestMailServerRelayDisallowed(TransactionCase):
    def test_switch_smtp_from(self):
        """Ensure all email sent are bpo-34424 and bpo-35805 free"""

        class FakeSMTP:
            """SMTP stub"""

            def __init__(self_):
                self_.email_sent = False
                self_.user = "allowed-user@text.example.com"

            # Python 3 before 3.7.4
            def sendmail(
                self_,
                smtp_from,
                smtp_to_list,
                message_str,
                mail_options=(),
                rcpt_options=(),
            ):
                self.assertEqual(smtp_from, self_.user)
                self_.email_sent = True

            # Python 3.7.4+
            def send_message(
                self_,
                message,
                smtp_from,
                smtp_to_list,
                mail_options=(),
                rcpt_options=(),
            ):
                self.assertEqual(smtp_from, self_.user)
                self_.email_sent = True

        msg = email.message.EmailMessage(policy=email.policy.SMTP)
        msg["From"] = '"Joé Doe" <joe@example.com>'
        msg["To"] = '"Joé Doe" <joe@example.com>'

        # Message-Id & References fields longer than 77 chars (bpo-35805)
        msg["Message-Id"] = (
            "<929227342217024.1596730490.324691772460938-"
            "example-30661-some.reference@test-123.example.com>"
        )
        msg["References"] = (
            "<345227342212345.1596730777.324691772483620-"
            "example-30453-other.reference@test-123.example.com>"
        )
        smtp = FakeSMTP()
        self.patch(threading.currentThread(), "testing", False)
        self.env["ir.mail_server"].send_email(msg, smtp_session=smtp)
        self.assertTrue(smtp.email_sent)
        self.assertEqual(msg["From"], "Joé Doe <allowed-user@text.example.com>")
