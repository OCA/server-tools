# -*- coding: utf-8 -*-
# Copyright 2016 Angel Moya (http://angelmoya.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
import openerp
from openerp import api


class TestAttachmentBaseSynchronize(TransactionCase):

    def setUp(self):
        super(TestAttachmentBaseSynchronize, self).setUp()
        self.registry.enter_test_mode()
        self.env = api.Environment(self.registry.test_cr, self.env.uid,
                                   self.env.context)
        self.attachment = self.env.ref(
            'attachment_base_synchronize.attachment_metadata')
        self.ir_attachment_metadata = self.env['ir.attachment.metadata']

    def tearDown(self):
        self.registry.leave_test_mode()
        super(TestAttachmentBaseSynchronize, self).tearDown()

    def test_attachment_metadata(self):
        """Test run_attachment_metadata_scheduler to ensure set state to done
        """
        self.assertEqual(
            self.attachment.state,
            'pending'
        )
        self.ir_attachment_metadata.run_attachment_metadata_scheduler()
        self.env.invalidate_all()
        with openerp.registry(self.env.cr.dbname).cursor() as new_cr:
            new_env = api.Environment(
                new_cr, self.env.uid, self.env.context)
            attach = self.attachment.with_env(new_env)
            self.assertEqual(
                attach.state,
                'done'
            )

    def test_set_done(self):
        """Test set_done manually
        """
        self.attachment.set_done()
        self.assertEqual(
            self.attachment.state,
            'done'
        )
