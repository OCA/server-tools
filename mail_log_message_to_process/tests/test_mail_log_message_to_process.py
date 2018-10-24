# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
#           (www.eficent.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.mail.tests.common import TestMail
from odoo.addons.mail.tests.test_mail_gateway import MAIL_TEMPLATE


class TestMailLogMessageToProcess(TestMail):

    def setUp(self):
        super(TestMailLogMessageToProcess, self).setUp()

        self.fetchmail_server = self.env['fetchmail.server'].create({
            'name': 'Test Fetchmail Server',
            'type': 'imap',
        })

    def test_message_process(self):
        email_from = 'test1@example.com'
        to_email = 'test2@example.com'
        msg_id = 'Test log message to process'
        with self.assertRaises(ValueError):
            mail = MAIL_TEMPLATE.format(
                to=to_email,
                email_from=email_from,
                cc='',
                subject='testing',
                extra='',
                msg_id=msg_id,
            )
            self.env['mail.thread'].with_context({
                'fetchmail_server_id': self.fetchmail_server.id,
            }).message_process(None, mail)
