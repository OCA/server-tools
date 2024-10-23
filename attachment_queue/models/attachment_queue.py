# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api, fields, models, registry

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
        help="Link to ir.attachment model ",
    )
    file_type = fields.Selection(
        selection=[],
        help="The file type determines an import method to be used "
        "to parse and transform data before their import in ERP or an export",
    )
    date_done = fields.Datetime()
    state = fields.Selection(
        [("pending", "Pending"), ("failed", "Failed"), ("done", "Done")],
        readonly=False,
        required=True,
        default="pending",
    )
    state_message = fields.Text()
    failure_emails = fields.Char(
        compute="_compute_failure_emails",
        string="Failure Emails",
        help="Comma-separated list of email addresses to be notified in case of"
        "failure",
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
                    new_env = api.Environment(new_cr, SUPERUSER_ID, self.env.context)
                    attach = attachment.with_env(new_env)
                    try:
                        attach._run()
                    # pylint: disable=broad-except
                    except Exception as e:
                        attach.env.cr.rollback()
                        _logger.exception(str(e))
                        attach.write({"state": "failed", "state_message": str(e)})
                        emails = attach.failure_emails
                        if emails:
                            failure_tmpl.send_mail(attach.id)
                        attach.env.cr.commit()
                    else:
                        vals = {
                            "state": "done",
                            "date_done": fields.Datetime.now(),
                            "state_message": None,
                        }
                        attach.write(vals)
                        attach.env.cr.commit()
        return True

    def _run(self):
        self.ensure_one()
        _logger.info("Starting processing of attachment queue id %d", self.id)

    def set_done(self):
        """
        Manually set to done
        """
        message = "Manually set to done by %s" % self.env.user.name
        self.write({"state_message": message, "state": "done"})
