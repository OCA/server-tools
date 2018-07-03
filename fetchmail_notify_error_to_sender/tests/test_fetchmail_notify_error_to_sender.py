# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import socket
from odoo.addons.mail.tests.common import TestMail
from odoo.addons.mail.tests.test_mail_gateway import MAIL_TEMPLATE
from odoo.tools import mute_logger


class TestFetchmailNotifyErrorToSender(TestMail):

    def setUp(self):
        super(TestFetchmailNotifyErrorToSender, self).setUp()

        self.fetchmail_server = self.env['fetchmail.server'].create({
            'name': 'Test Fetchmail Server',
            'type': 'imap',
            'error_notice_template_id': self.env.ref('%s.%s' % (
                'fetchmail_notify_error_to_sender',
                'email_template_error_notice',
            )).id
        })

    def format_and_process_with_context(
        self, template, to_email='groups@example.com, other@gmail.com',
        subject='Frogs', extra='',
        email_from='Sylvie Lelitre <test.sylvie.lelitre@agrolait.com>',
        cc_email='',
        msg_id='<1198923581.41972151344608186760.JavaMail@agrolait.com>',
        model=None, target_model='mail.test', target_field='name', ctx=False,
    ):
        self.assertFalse(self.env[target_model].search([
            (target_field, '=', subject),
        ]))
        mail = template.format(
            to=to_email,
            subject=subject,
            cc=cc_email,
            extra=extra,
            email_from=email_from,
            msg_id=msg_id,
        )
        self.env['mail.thread'].with_context(ctx or {}).message_process(
            model,
            mail,
        )
        return self.env[target_model].search([(target_field, '=', subject)])

    @mute_logger('odoo.addons.mail.models.mail_thread', 'odoo.models')
    def test_message_process(self):
        email_from = 'valid.lelitre@agrolait.com'

        count_return_mails_before = self.env['mail.mail'].search_count([
            ('email_to', '=', email_from),
        ])

        with self.assertRaises(ValueError):
            self.format_and_process_with_context(
                MAIL_TEMPLATE,
                email_from=email_from,
                to_email='noone@example.com',
                subject='spam',
                extra='In-Reply-To: <12321321-openerp-%d-mail.test@%s>' % (
                    self.test_public.id,
                    socket.gethostname(),
                ),
                ctx={
                    'fetchmail_server_id': self.fetchmail_server.id,
                }
            )

        count_return_mails_after = self.env['mail.mail'].search_count([
            ('email_to', '=', email_from),
        ])
        self.assertEqual(
            count_return_mails_after,
            count_return_mails_before + 1,
        )
