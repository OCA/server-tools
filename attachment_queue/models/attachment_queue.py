# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models, registry

_logger = logging.getLogger(__name__)


class AttachmentQueue(models.Model):
    _name = "attachment.queue"
    _description = "Attachment Queue"
    _inherits = {"ir.attachment": "attachment_id"}
    _inherit = ["mail.thread"]

    attachment_id = fields.Many2one(
        "ir.attachment",
        required=True,
        ondelete="cascade",
        help="Link to the related ir.attachment model",
    )
    file_type = fields.Selection(
        selection=[],
        help="Operations are realized on 'Attachments Queues' objects depending on "
        "their 'File Type' value.",
    )
    done_date = fields.Datetime()
    done_uid = fields.Many2one("res.users")
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("done", "Done"),
            ("failed", "Failed"),
            ("cancel", "Cancelled"),
        ],
        readonly=False,
        required=True,
        default="pending",
        track_visibility="onchange",
    )
    error_message = fields.Text()
    failure_emails = fields.Char(
        compute="_compute_failure_emails",
        string="Failure Emails",
        help="Comma-separated list of email addresses to be notified in case of"
        "operation failure on an 'Attachment Queue' object.",
    )

    def _compute_failure_emails(self):
        for attach in self:
            attach.failure_emails = attach._get_failure_emails()

    def _get_failure_emails(self):
        # to be overriden in submodules implementing the file_type
        self.ensure_one()
        return ""

    @api.model
    def run_attachment_queue_scheduler(self, domain=None):
        if domain is None:
            domain = [("state", "=", "pending")]
        batch_limit = self.env.ref(
            "attachment_queue.attachment_queue_cron_batch_limit"
        ).value
        if batch_limit and batch_limit.isdigit():
            limit = int(batch_limit)
        else:
            limit = 200
        attachments = self.search(domain, limit=limit)
        if attachments:
            return attachments.run()
        return True

    def run(self):
        """
        Run the process for each attachment queue
        """
        failure_tmpl = self.env.ref("attachment_queue.attachment_failure_notification")
        for attachment in self:
            with api.Environment.manage():
                with registry(self.env.cr.dbname).cursor() as new_cr:
                    new_env = api.Environment(new_cr, self.env.uid, self.env.context)
                    attach = attachment.with_env(new_env)
                    try:
                        attach._run()
                    # pylint: disable=broad-except
                    except Exception as e:
                        attach.env.cr.rollback()
                        _logger.exception(str(e))
                        attach.write({"state": "failed", "error_message": str(e)})
                        emails = attach.failure_emails
                        if emails:
                            failure_tmpl.send_mail(attach.id)
                        attach.env.cr.commit()
                    else:
                        vals = {
                            "state": "done",
                            "done_date": fields.Datetime.now(),
                            "done_uid": self.env.user.id,
                        }
                        attach.write(vals)
                        attach.env.cr.commit()
        return True

    def _run(self):
        self.ensure_one()
        _logger.info("Starting processing of attachment queue id %d", self.id)

    def cancel(self):
        """Manually cancel operation on attachment"""
        self.write({"state": "cancel"})

    def reset_pending(self):
        """Manually reset state to "Pending" """
        self.write({"state": "pending"})
