# Copyright 2025 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon

MAIL_TEMPLATE = """Return-Path: <whatever-2a840@postmaster.twitter.com>
To: {to}
Received: by mail1.openerp.com (Postfix, from userid 10002)
    id 5DF9ABFB2A; Fri, 30 May 2025 16:16:39 +0200 (CEST)
From: {email_from}
Subject: {subject}
MIME-Version: 1.0
Content-Type: multipart/alternative;
    boundary="----=_Part_4200734_24778174.1344608186754"
Date: Fri, 30 May 2025 14:16:26 +0000
Message-ID: {msg_id}
------=_Part_4200734_24778174.1344608186754
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: quoted-printable

Testing FetchMail Notify Error To Sender!

--
Your Dear Customer
------=_Part_4200734_24778174.1344608186754
Content-Type: text/html; charset=utf-8
Content-Transfer-Encoding: quoted-printable

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
 <head>=20
  <meta http-equiv=3D"Content-Type" content=3D"text/html; charset=3Dutf-8" />
 </head>=20
 <body style=3D"background: #ffffff;-webkit-text-size-adjust: 100%;">=20

  <p>Testing FetchMail Notify Error To Sender!</p>

  <p>--<br/>
     Your Dear Customer
  <p>
 </body>
</html>
------=_Part_4200734_24778174.1344608186754--
"""


class TestFetchmailNotifyErrorToSender(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fetchmail_server = cls.env["fetchmail.server"].create(
            [
                {
                    "name": "Test Server",
                    "server_type": "pop",
                    "server": "test",
                    "port": 110,
                    "user": "test",
                    "password": "test",
                    "state": "done",
                }
            ]
        )

    def message_process(self, fetchmail_server_id=None):
        MailThread = self.env["mail.thread"]
        message = MAIL_TEMPLATE.format(
            to="test@123.com",
            subject="Test Fetchmail Error Notification",
            email_from=self.env.user.email,
            msg_id="168242744424.20.2028152230359369389@dd607af32154",
        )
        if fetchmail_server_id:
            MailThread = MailThread.with_context(
                default_fetchmail_server_id=fetchmail_server_id
            )
        MailThread.message_process(
            model=None,
            message=message,
        )

    def test_fetchmail_notify_error_without_fetchmail_server(self):
        with self.assertRaises(ValueError):
            self.message_process()

    def test_fetchmail_notify_error_with_fetchmail(self):
        self.fetchmail_server.error_notice_template_id = False
        with self.assertRaises(ValueError):
            self.message_process(fetchmail_server_id=self.fetchmail_server.id)
        self.fetchmail_server.error_notice_template_id = self.env.ref(
            "fetchmail_notify_error_to_sender.email_template_error_notice"
        )
        with self.assertRaises(ValueError):
            self.message_process(fetchmail_server_id=self.fetchmail_server.id)
