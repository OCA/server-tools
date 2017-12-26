# coding: utf-8
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase
from odoo.addons.mail.tests.test_mail_gateway import (
    MAIL_MULTIPART_MIXED, MAIL_MULTIPART_MIXED_TWO)


class TestFetchmailInbox(TransactionCase):
    def setUp(self):
        super(TestFetchmailInbox, self).setUp()
        self.env['fetchmail.inbox'].search([]).unlink()

    def message_process(self, mail):
        self.env['mail.thread'].with_context(
            mail_channel_noautofollow=True).message_process(
                'fetchmail.inbox', mail)

    def test_fetchmail_inbox(self):
        """ Processing fetchmail inbox will create a new record.
        The origin email and its attachments will be moved over. """
        def get_needaction():
            menu = self.env.ref('fetchmail_inbox.menu_inbox')
            return menu.get_needaction_data()[menu.id]['needaction_counter']

        self.message_process(MAIL_MULTIPART_MIXED)
        inbox1 = self.env['fetchmail.inbox'].search([])
        self.assertTrue(inbox1)
        self.assertEqual(len(inbox1.message_ids), 1)
        self.assertEqual(inbox1.name_get(),
                         [(inbox1.id, 'Test mail multipart/mixed')])

        # Needaction counter is independent of read status
        self.assertEqual(get_needaction(), 1)
        inbox1.message_ids.is_read = True
        self.assertEqual(get_needaction(), 1)

        message1 = inbox1.message_ids
        attachment1 = self.env['ir.attachment'].search(
            [('res_model', '=', inbox1._name), ('res_id', '=', inbox1.id)])
        self.assertEqual(len(attachment1), 1)
        self.assertTrue(attachment1.name, 'thetruth.pdf')

        action = message1.with_context(
            set_default_res_model='res.partner').fetchmail_inbox_create()
        partner_id = action['res_id']
        partner = self.env['res.partner'].browse(partner_id)
        self.assertIn(message1, partner.message_ids)
        self.assertIn(
            attachment1, self.env['ir.attachment'].search([
                ('res_model', '=', 'res.partner'),
                ('res_id', '=', partner_id)]))

        # Now attach a second message to the existing partner
        self.message_process(MAIL_MULTIPART_MIXED_TWO)
        inbox2 = self.env['fetchmail.inbox'].search([('id', '>', inbox1.id)])
        self.assertTrue(inbox2)
        self.assertEqual(len(inbox2.message_ids), 1)
        message2 = inbox2.message_ids
        attachment2 = self.env['ir.attachment'].search(
            [('res_model', '=', inbox2._name), ('res_id', '=', inbox2.id)])
        self.assertEqual(len(attachment2), 1)

        self.env['fetchmail.inbox.attach.existing.wizard'].create({
            'res_model': 'res.partner',
            'res_id': partner_id,
            'mail_id': message2.id,
        }).button_attach()
        self.assertIn(message2, partner.message_ids)
        self.assertIn(
            attachment2, self.env['ir.attachment'].search([
                ('res_model', '=', 'res.partner'),
                ('res_id', '=', partner_id)]))

    def test_fields_view_get(self):
        """ The reference field is set to the model in the context """
        attach_model = self.env['fetchmail.inbox.attach.existing.wizard']
        res = attach_model.with_context(
            set_default_res_model='res.partner').fields_view_get()
        self.assertEqual(res['fields']['res_id']['type'], 'many2one')
        self.assertEqual(res['fields']['res_id']['relation'], 'res.partner')

    def test_name_get_no_message(self):
        inbox = self.env['fetchmail.inbox'].create({})
        self.assertEqual(inbox.name_get(), [(inbox.id, 'Fetchmail inbox')])
