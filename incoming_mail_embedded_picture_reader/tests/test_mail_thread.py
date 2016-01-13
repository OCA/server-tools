# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from email.message import Message
from openerp.tests.common import TransactionCase


class TestMailThread(TransactionCase):

    def setUp(self):
        super(TestMailThread, self).setUp()
        self.mail_thread = self.env['mail.thread']

    def test_get_attachment_data(self):
        file_name = 'filename'
        cid_void = '42'
        cid = '<%s>' % cid_void
        part = Message()
        res = self.mail_thread._get_attachment_data(file_name, part)
        self.assertEqual(res[0], file_name, 'Should be the same')
        part.add_header('content-id', cid)
        res = self.mail_thread._get_attachment_data(file_name, part)
        self.assertEqual(
            '%s<%s>' % (file_name, cid_void), res[0], 'Should be the same')
