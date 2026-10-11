# Copyright 2026 Ledo Enterprises
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

import boto3
from botocore.exceptions import ClientError

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class FetchmailServer(models.Model):
    _inherit = "fetchmail.server"

    server_type = fields.Selection(
        selection_add=[("s3", "S3 Bucket (AWS SES / S3-compatible)")],
        ondelete={"s3": "set default"},
    )
    s3_bucket = fields.Char("S3 Bucket Name")
    s3_prefix = fields.Char(
        "Object Key Prefix",
        default="emails/",
        help="Only process objects under this prefix.",
    )
    s3_region = fields.Char("AWS Region", default="us-east-1")
    s3_access_key = fields.Char("Access Key ID")
    s3_secret_key = fields.Char("Secret Access Key")
    s3_endpoint_url = fields.Char(
        "Endpoint URL",
        help="For S3-compatible services (MinIO, Hetzner, etc.). "
        "Leave empty for AWS S3.",
    )
    s3_archive_prefix = fields.Char(
        "Archive Prefix",
        default="processed/",
        help="Move processed emails here instead of deleting. "
        "Leave empty to delete after processing.",
    )

    def _compute_server_type_info(self):
        s3_servers = self.filtered(lambda s: s.server_type == "s3")
        s3_servers.server_type_info = _(
            "Poll an S3-compatible bucket for raw email files (.eml). "
            "Typically used with AWS SES inbound email rules that store "
            "messages in S3. Processed emails are archived or deleted."
        )
        return super(FetchmailServer, self - s3_servers)._compute_server_type_info()

    @api.onchange("server_type", "is_ssl", "object_id")
    def onchange_server_type(self):
        if self.server_type == "s3":
            self.server = False
            self.port = 0
            self.is_ssl = False
            return
        return super().onchange_server_type()

    def _get_connection_type(self):
        self.ensure_one()
        if self.server_type == "s3":
            return "s3"
        return super()._get_connection_type()

    def _get_s3_client(self):
        """Create and return a boto3 S3 client."""
        self.ensure_one()
        kwargs = {"region_name": self.s3_region or "us-east-1"}
        if self.s3_access_key and self.s3_secret_key:
            kwargs["aws_access_key_id"] = self.s3_access_key
            kwargs["aws_secret_access_key"] = self.s3_secret_key
        if self.s3_endpoint_url:
            kwargs["endpoint_url"] = self.s3_endpoint_url
        return boto3.client("s3", **kwargs)

    def connect(self, allow_archived=False):
        self.ensure_one()
        if self._get_connection_type() == "s3":
            if not allow_archived and not self.active:
                raise UserError(
                    _(
                        'The server "%s" cannot be used because it is archived.',
                        self.display_name,
                    )
                )
            return self._get_s3_client()
        return super().connect(allow_archived=allow_archived)

    def button_confirm_login(self):
        s3_servers = self.filtered(lambda s: s._get_connection_type() == "s3")
        for server in s3_servers:
            try:
                client = server._get_s3_client()
                client.list_objects_v2(
                    Bucket=server.s3_bucket,
                    Prefix=server.s3_prefix or "",
                    MaxKeys=1,
                )
                server.write({"state": "done"})
            except ClientError as e:
                raise UserError(
                    _("S3 connection failed:\n%s", e.response["Error"]["Message"])
                ) from e
            except Exception as e:
                raise UserError(_("S3 connection test failed:\n%s", str(e))) from e
        non_s3 = self - s3_servers
        if non_s3:
            return super(FetchmailServer, non_s3).button_confirm_login()
        return True

    def fetch_mail(self, raise_exception=True):
        """Extend fetch_mail to handle S3 server type."""
        s3_servers = self.filtered(lambda s: s._get_connection_type() == "s3")
        non_s3 = self - s3_servers
        for server in s3_servers:
            server._fetch_mail_s3(raise_exception=raise_exception)
        if non_s3:
            return super(FetchmailServer, non_s3).fetch_mail(
                raise_exception=raise_exception
            )
        return True

    def _fetch_mail_s3(self, raise_exception=True):
        """Fetch and process emails from an S3 bucket."""
        self.ensure_one()
        _logger.info(
            "Start checking for new emails on S3 server %s (bucket: %s, prefix: %s)",
            self.name,
            self.s3_bucket,
            self.s3_prefix,
        )
        context = {
            "fetchmail_cron_running": True,
            "default_fetchmail_server_id": self.id,
        }
        MailThread = self.env["mail.thread"]
        count, failed = 0, 0
        try:
            client = self._get_s3_client()
            paginator = client.get_paginator("list_objects_v2")
            for page in paginator.paginate(
                Bucket=self.s3_bucket, Prefix=self.s3_prefix or ""
            ):
                for obj in page.get("Contents", []):
                    key = obj["Key"]
                    if key.endswith("/"):
                        continue
                    try:
                        response = client.get_object(Bucket=self.s3_bucket, Key=key)
                        raw_email = response["Body"].read()
                    except ClientError:
                        _logger.warning(
                            "Failed to download S3 object %s", key, exc_info=True
                        )
                        failed += 1
                        continue
                    try:
                        MailThread.with_context(**context).message_process(
                            self.object_id.model,
                            raw_email,
                            save_original=self.original,
                            strip_attachments=(not self.attach),
                        )
                    except Exception:
                        _logger.info(
                            "Failed to process mail from S3 key %s",
                            key,
                            exc_info=True,
                        )
                        failed += 1
                        if not tools.config["test_enable"]:
                            self.env.cr.commit()  # pylint: disable=invalid-commit
                        continue
                    self._s3_handle_processed(client, key)
                    if not tools.config["test_enable"]:
                        self.env.cr.commit()  # pylint: disable=invalid-commit
                    count += 1
            _logger.info(
                "Fetched %d email(s) on S3 server %s; %d succeeded, %d failed.",
                count,
                self.name,
                count - failed,
                failed,
            )
        except Exception as e:
            if raise_exception:
                raise UserError(_("Couldn't fetch emails from S3:\n%s", str(e))) from e
            _logger.info(
                "General failure fetching from S3 server %s.",
                self.name,
                exc_info=True,
            )

    def _s3_handle_processed(self, client, key):
        """Archive or delete a processed S3 object."""
        self.ensure_one()
        try:
            if self.s3_archive_prefix:
                filename = key.rsplit("/", 1)[-1]
                archive_key = f"{self.s3_archive_prefix}{filename}"
                client.copy_object(
                    Bucket=self.s3_bucket,
                    CopySource={"Bucket": self.s3_bucket, "Key": key},
                    Key=archive_key,
                )
            client.delete_object(Bucket=self.s3_bucket, Key=key)
        except ClientError:
            _logger.warning("Failed to archive/delete S3 object %s", key, exc_info=True)
