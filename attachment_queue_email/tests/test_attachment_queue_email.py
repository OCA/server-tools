# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.test_mail.tests.test_mail_gateway import TestMailgateway
from odoo.addons.test_mail.data.test_mail_data import (
    MAIL_MULTIPART_IMAGE,
    MAIL_SINGLE_BINARY,
)


class TestAttachmentQueueEmail(TestMailgateway):
    def setUp(self):
        super().setUp()
        self.attach_condition_1 = self.env["fetchmail.attachment.condition"].create(
            {
                "name": "Attchment Condition 1",
                "email_from": "Bruce Wayne",
                "file_extension": ".pdf",
            }
        )
        self.attach_condition_2 = self.env["fetchmail.attachment.condition"].create(
            {
                "name": "Attchment Condition 2",
                "email_subject": "Wonderful pictures",
                "file_extension": ".gif",
            }
        )

        self.attach_queue_model = self.env["ir.model"].search(
            [("model", "=", "attachment.queue")]
        )
        self.fetchmail_server = self.env["fetchmail.server"].create(
            {
                "name": "Test Fetchmail Server 1",
                "type": "imap",
                "attach": True,
                "object_id": self.attach_queue_model.id,
                "attachment_condition_ids": [
                    (6, 0, [self.attach_condition_1.id, self.attach_condition_2.id])
                ],
            }
        )
        self.context_server = {
            "fetchmail_server_id": self.fetchmail_server.id,
            "server_type": self.fetchmail_server.type,
        }

    def test_message_single_binary(self):
        """Run message_process on emails with attachment check if an attachment_queue
        is created
        """
        self.assertFalse(
            self.env["attachment.queue"].search([("datas_fname", "=", "thetruth.pdf")])
        )

        self.env["mail.thread"].with_context(self.context_server).message_process(
            self.fetchmail_server.object_id.model, MAIL_SINGLE_BINARY,
        )

        attach_queue = self.env["attachment.queue"].search(
            [("datas_fname", "=", "thetruth.pdf")]
        )
        self.assertEqual(len(attach_queue), 1)
        self.assertEqual(attach_queue.datas, b"SSBhbSB0aGUgQmF0TWFuCg==")

    def test_message_multi_image(self):
        mail = MAIL_MULTIPART_IMAGE.format(subject="Wonderful pictures", to="")

        self.env["mail.thread"].with_context(self.context_server).message_process(
            self.fetchmail_server.object_id.model, mail,
        )
        attach_queues = self.env["attachment.queue"].search(
            [("datas_fname", "like", ".gif")]
        )
        self.assertEqual(len(attach_queues), 3)
        self.assertEqual(attach_queues[0].datas_fname, "orangée.gif")
