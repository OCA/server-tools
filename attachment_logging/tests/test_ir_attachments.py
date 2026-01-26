import json
import tempfile

from odoo.http import Request
from odoo.tools.misc import format_datetime

from odoo.addons.base.tests.common import HttpCaseWithUserDemo


class TestIrAttachments(HttpCaseWithUserDemo):
    def _make_rpc(self, route, params, headers=None):
        data = json.dumps(
            {
                "id": 0,
                "jsonrpc": "2.0",
                "method": "call",
                "params": params,
            }
        ).encode()
        headers = headers or {}
        headers["Content-Type"] = "application/json"
        return self.url_open(route, data, headers=headers)

    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Test Partner #1"})
        self.mt_attachment = self.env.ref("attachment_logging.mt_attachment")

    def _attach_temp_file(self):
        """Attach temp file to partner record"""
        with tempfile.NamedTemporaryFile(mode="rb") as f:
            response = self.url_open(
                url=f"{self.base_url()}/mail/attachment/upload",
                data={
                    "thread_id": self.partner.id,
                    "thread_model": "res.partner",
                    "csrf_token": Request.csrf_token(self),
                },
                files={"ufile": f},
            )
            return response

    def _delete_attachment(self, attachment_id):
        """Delete attachment from partner record"""
        response = self._make_rpc(
            f"{self.base_url()}/mail/attachment/delete",
            {
                "attachment_id": attachment_id,
            },
        )
        return response

    def test_upload_file_without_config(self):
        """Test flow where upload temp file to record (default behavior)"""
        self.authenticate("demo", "demo")
        message_count = len(self.partner.message_ids)
        response = self._attach_temp_file()
        data = response.json()
        self.assertEqual(
            response.status_code, 200, "Response status code must be equal to 200 (OK)"
        )
        attachments = self.env["ir.attachment"].search(
            [
                ("res_id", "=", self.partner.id),
                ("res_model", "=", "res.partner"),
            ]
        )
        self.assertEqual(len(attachments), 1, "Count attachment must be equal to 1")
        self.assertEqual(
            data.get("id"), attachments.id, "Attachment ID must be the same"
        )
        self.assertEqual(
            data.get("create_user"),
            attachments.create_uid.name,
            "Attachment create user name must be the same",
        )
        self.assertEqual(
            data.get("create_date"),
            format_datetime(self.env, attachments.create_date),
            "Attachment create date must be the same",
        )
        self.assertEqual(
            len(self.partner.message_ids),
            message_count,
            "Message count must be the same",
        )

    def test_upload_file_with_config(self):
        """Test flow where upload temp file to record with log message"""
        self.authenticate("demo", "demo")
        message_count = len(self.partner.message_ids)
        self.env["ir.config_parameter"].sudo().set_param(
            "attachment_logging.use_attachment_log", True
        )
        response = self._attach_temp_file()
        data = response.json()
        self.assertEqual(
            response.status_code, 200, "Response status code must be equal to 200 (OK)"
        )
        attachments = self.env["ir.attachment"].search(
            [
                ("res_id", "=", self.partner.id),
                ("res_model", "=", "res.partner"),
            ]
        )
        self.assertEqual(len(attachments), 1, "Count attachment must be equal to 1")
        self.assertEqual(
            data.get("id"), attachments.id, "Attachment ID must be the same"
        )
        attachment_addition_data = attachments.get_additional_data()
        self.assertEqual(
            data.get("create_user"),
            attachment_addition_data.get("create_user"),
            "Attachment authors must be the same",
        )
        self.assertEqual(
            data.get("create_date"),
            attachment_addition_data.get("create_date"),
            "Dates must be the same",
        )
        self.assertNotEqual(
            len(self.partner.message_ids),
            message_count,
            "Message count must not be the same",
        )
        last_message = self.partner.message_ids[0]
        self.assertEqual(
            last_message.subtype_id,
            self.mt_attachment,
            "Message subtypes must be the same",
        )
        self.assertEqual(
            last_message.author_id,
            self.env.ref("base.user_root").partner_id,
            "Message author must be OdooBot",
        )
        self.assertIn(
            "attached", last_message.body, "Message body must be contain 'attached'"
        )

    def test_delete_attachment_without_config(self):
        """Test flow where delete attachment from record (default behavior)"""
        self.authenticate("demo", "demo")
        message_count = len(self.partner.message_ids)
        response = self._attach_temp_file()
        data = response.json()
        attachments = self.env["ir.attachment"].search(
            [
                ("res_id", "=", self.partner.id),
                ("res_model", "=", "res.partner"),
            ]
        )
        self.assertEqual(len(attachments), 1, "Count attachment must be equal to 1")
        self.assertEqual(
            response.status_code, 200, "Response status code must be equal to 200 (OK)"
        )
        self._delete_attachment(attachment_id=data["id"])
        attachments = self.env["ir.attachment"].search(
            [
                ("res_id", "=", self.partner.id),
                ("res_model", "=", "res.partner"),
            ]
        )
        self.assertFalse(attachments, "Attachments must be empty")
        self.assertEqual(
            len(self.partner.message_ids),
            message_count,
            "Message count must be the same",
        )

    def test_delete_attachment_with_config(self):
        """Test flow where delete attachment from record with log message"""
        self.authenticate("demo", "demo")
        message_count = len(self.partner.message_ids)
        self.env["ir.config_parameter"].sudo().set_param(
            "attachment_logging.use_attachment_log", True
        )
        response = self._attach_temp_file()
        data = response.json()
        self.assertEqual(
            response.status_code, 200, "Response status code must be equal to 200 (OK)"
        )
        self._delete_attachment(attachment_id=data["id"])
        attachments = self.env["ir.attachment"].search(
            [
                ("res_id", "=", self.partner.id),
                ("res_model", "=", "res.partner"),
            ]
        )
        self.assertFalse(attachments, "Attachments must be empty")
        self.assertNotEqual(
            len(self.partner.message_ids),
            message_count,
            "Message count must not be the same",
        )
        last_message = self.partner.message_ids[0]
        self.assertEqual(
            last_message.subtype_id,
            self.mt_attachment,
            "Message subtypes must be the same",
        )
        self.assertEqual(
            last_message.author_id,
            self.env.ref("base.user_root").partner_id,
            "Message author must be OdooBot",
        )
        self.assertIn(
            "unlinked", last_message.body, "Message body must be contain 'unlinked'"
        )
