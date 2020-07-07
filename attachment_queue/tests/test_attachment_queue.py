# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo
from odoo import api
from odoo.tests.common import TransactionCase


class TestAttachmentBaseQueue(TransactionCase):
    def setUp(self):
        super().setUp()
        self.registry.enter_test_mode(self.env.cr)
        self.env = api.Environment(
            self.registry.test_cr, self.env.uid, self.env.context
        )
        self.attachment = self.env.ref(
            "attachment_queue.attachment_queue_demo"
        )

    def tearDown(self):
        self.registry.leave_test_mode()
        super().tearDown()

    def test_attachment_queue(self):
        """Test run_attachment_queue_scheduler to ensure set state to done
        """
        self.assertEqual(self.attachment.state, "pending")
        self.env["attachment.queue"].run_attachment_queue_scheduler()
        self.env.cache.invalidate()
        with odoo.registry(self.env.cr.dbname).cursor() as new_cr:
            new_env = api.Environment(new_cr, self.env.uid, self.env.context)
            attach = self.attachment.with_env(new_env)
            self.assertEqual(attach.state, "done")

    def test_set_done(self):
        """Test set_done manually
        """
        self.assertEqual(self.attachment.state, "pending")
        self.attachment.set_done()
        self.assertEqual(self.attachment.state, "done")
