# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

from odoo.addons.queue_job.exception import RetryableJobError

_logger = logging.getLogger(__name__)

DEFAULT_ETA_FOR_RETRY = 60 * 60
STR_ERR_ATTACHMENT_RUNNING = (
    "The attachment is currently flagged as being in processing"
)
STR_ERROR_DURING_PROCESSING = "Error during processing of attachment_queue id {}: \n"


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
        help="Comma-separated list of email addresses to be notified in case of"
        "failure",
    )
    running_lock = fields.Boolean()

    @property
    def _eta_for_retry(self):
        return DEFAULT_ETA_FOR_RETRY

    @property
    def _job_attrs(self):
        return {"channel": "Attachment queues"}

    def _schedule_jobs(self):
        for el in self:
            el.with_delay(**self._job_attrs).run()

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res._schedule_jobs()
        return res

    def button_reschedule(self):
        self.state = "pending"
        self.state_message = ""
        self._schedule_jobs()

    def button_manual_run(self):
        if self.running_lock:
            raise UserError(STR_ERR_ATTACHMENT_RUNNING)
        self.run()

    def _compute_failure_emails(self):
        for attach in self:
            attach.failure_emails = attach._get_failure_emails()

    def _get_failure_emails(self):
        # to be overriden in submodules implementing the file_type
        self.ensure_one()
        return ""

    def run(self):
        """
        Run the process for an individual attachment queue
        """
        if self.state != "pending":
            return
        if self.running_lock is True:
            raise RetryableJobError(
                STR_ERR_ATTACHMENT_RUNNING, seconds=self._eta_for_retry
            )
        self.running_lock = True
        self.flush_recordset()
        try:
            with self.env.cr.savepoint():
                self._run()
        except Exception as e:
            _logger.warning(STR_ERROR_DURING_PROCESSING.format(self.id) + str(e))
            self.write(
                {"state": "failed", "state_message": str(e), "running_lock": False}
            )
            emails = self.failure_emails
            if emails:
                self.env.ref(
                    "attachment_queue.attachment_failure_notification"
                ).send_mail(self.id)
            return False
        else:
            self.write(
                {
                    "state": "done",
                    "date_done": fields.Datetime.now(),
                    "running_lock": False,
                }
            )
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
