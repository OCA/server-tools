# Copyright 2026 Ledo Enterprises
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from email.message import EmailMessage
from unittest.mock import MagicMock, patch

from odoo.tests import tagged

from odoo.addons.mail.tests.common import MailCommon


@tagged("post_install", "-at_install")
class TestFetchmailS3(MailCommon):
    def setUp(self):
        super().setUp()
        self.server = self.env["fetchmail.server"].create(
            {
                "name": "Test S3 Server",
                "server_type": "s3",
                "s3_bucket": "test-bucket",
                "s3_prefix": "emails/",
                "s3_region": "us-east-1",
                "s3_access_key": "AKIATEST",
                "s3_secret_key": "secret123",
                "s3_archive_prefix": "processed/",
                "object_id": self.env.ref("mail.model_discuss_channel").id,
            }
        )

    def _make_raw_email(self, subject="Test Email", body="Hello from S3"):
        """Build a minimal RFC822 email as bytes."""
        msg = EmailMessage()
        msg["From"] = "sender@example.com"
        msg["To"] = "test@docs.ledoweb.com"
        msg["Subject"] = subject
        msg.set_content(body)
        return msg.as_bytes()

    def _mock_s3_client(self, objects=None):
        """Return a mocked boto3 S3 client."""
        client = MagicMock()
        if objects is None:
            objects = []
        paginator = MagicMock()
        paginator.paginate.return_value = [
            {"Contents": [{"Key": key} for key in objects]}
        ]
        client.get_paginator.return_value = paginator
        for key in objects:
            body = MagicMock()
            body.read.return_value = self._make_raw_email(subject=f"Email: {key}")
            client.get_object.return_value = {"Body": body}
        client.list_objects_v2.return_value = {"KeyCount": len(objects)}
        return client

    @patch("odoo.addons.fetchmail_s3.models.fetchmail_server.boto3")
    def test_connection_type(self, mock_boto3):
        self.assertEqual(self.server._get_connection_type(), "s3")

    @patch("odoo.addons.fetchmail_s3.models.fetchmail_server.boto3")
    def test_button_confirm_login(self, mock_boto3):
        mock_client = MagicMock()
        mock_client.list_objects_v2.return_value = {"KeyCount": 0}
        mock_boto3.client.return_value = mock_client
        self.server.button_confirm_login()
        self.assertEqual(self.server.state, "done")
        mock_client.list_objects_v2.assert_called_once()

    @patch("odoo.addons.fetchmail_s3.models.fetchmail_server.boto3")
    def test_fetch_mail_empty_bucket(self, mock_boto3):
        mock_boto3.client.return_value = self._mock_s3_client(objects=[])
        self.server.write({"state": "done"})
        self.server.fetch_mail()

    @patch("odoo.addons.fetchmail_s3.models.fetchmail_server.boto3")
    def test_fetch_mail_processes_email(self, mock_boto3):
        mock_client = self._mock_s3_client(objects=["emails/msg001"])
        mock_boto3.client.return_value = mock_client
        self.server.write({"state": "done"})
        self.server.fetch_mail()
        # Verify the email was archived (copy + delete)
        mock_client.copy_object.assert_called_once()
        mock_client.delete_object.assert_called_once()

    @patch("odoo.addons.fetchmail_s3.models.fetchmail_server.boto3")
    def test_fetch_mail_delete_without_archive(self, mock_boto3):
        self.server.write({"s3_archive_prefix": False, "state": "done"})
        mock_client = self._mock_s3_client(objects=["emails/msg002"])
        mock_boto3.client.return_value = mock_client
        self.server.fetch_mail()
        # No copy, only delete
        mock_client.copy_object.assert_not_called()
        mock_client.delete_object.assert_called_once()

    @patch("odoo.addons.fetchmail_s3.models.fetchmail_server.boto3")
    def test_skips_directory_keys(self, mock_boto3):
        mock_client = self._mock_s3_client(objects=["emails/", "emails/msg003"])
        mock_boto3.client.return_value = mock_client
        self.server.write({"state": "done"})
        self.server.fetch_mail()
        # Only msg003 should be fetched, not the "directory" key
        mock_client.get_object.assert_called_once()
