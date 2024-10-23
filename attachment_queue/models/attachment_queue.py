# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

import psycopg2

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.queue_job.exception import RetryableJobError

_logger = logging.getLogger(__name__)

DEFAULT_ETA_FOR_RETRY = 60 * 60
STR_ERR_ATTACHMENT_RUNNING = "The attachment is currently being in processing"
STR_ERROR_DURING_PROCESSING = "Error during processing of attachment_queue id {}: \n"


class AttachmentQueue(models.Model):
    _name = "attachment.queue"
    _description = "Attachment Queue"
    _inherits = {"ir.attachment": "attachment_id"}
    _inherit = ["mail.thread", "mail.activity.mixin"]

    attachment_id = fields.Many2one(
        "ir.attachment",
        required=True,
        ondelete="cascade",
        help="Link to ir.attachment model ",
    )
    file_type = fields.Selection(
        selection=[],
        index="btree",
        help="The file type determines an import method to be used "
        "to parse and transform data before their import in ERP or an export",
    )
    date_done = fields.Datetime()
    state = fields.Selection(
        [("pending", "Pending"), ("failed", "Failed"), ("done", "Done")],
        readonly=False,
        required=True,
        default="pending",
        index="btree",
    )
    state_message = fields.Text()
    failure_emails = fields.Char(
        compute="_compute_failure_emails",
        help="Comma-separated list of email addresses to be notified in case of"
        "failure",
    )

    def _job_attrs(self):
        # Override this method to have file type specific job attributes
        self.ensure_one()
        return {"channel": "root.attachment_queue"}

    def _schedule_jobs(self):
        for el in self:
            kwargs = el._job_attrs()
            el.with_delay(**kwargs).run_as_job()

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res._schedule_jobs()
        return res

    def button_reschedule(self):
        self.write({"state": "pending", "state_message": ""})
        self._schedule_jobs()

    def _compute_failure_emails(self):
        for attach in self:
            attach.failure_emails = attach._get_failure_emails()

    def _get_failure_emails(self):
        # to be overriden in submodules implementing the file_type
        self.ensure_one()
        return ""

    def button_manual_run(self):
        """
        Run the process for an individual attachment queue from a dedicated button
        """
        try:
            self._cr.execute(
                """
                SELECT id
                FROM attachment_queue
                WHERE id  = %s
                FOR UPDATE NOWAIT
            """,
                (self.id,),
            )
        except psycopg2.OperationalError as exc:
            raise UserError(_(STR_ERR_ATTACHMENT_RUNNING)) from exc
        if self.state != "done":
            self.run()

    def run_as_job(self):
        """Run the process for an individual attachment queue from a async job"""
        try:
            self._cr.execute(
                """
                SELECT id
                FROM attachment_queue
                WHERE id  = %s
                FOR UPDATE NOWAIT
            """,
                (self.id,),
            )
        except psycopg2.OperationalError as exc:
            raise RetryableJobError(
                STR_ERR_ATTACHMENT_RUNNING,
                seconds=DEFAULT_ETA_FOR_RETRY,
                ignore_retry=True,
            ) from exc
        if self.state == "pending":
            try:
                with self.env.cr.savepoint():
                    self.run()
            except Exception as e:
                _logger.warning(STR_ERROR_DURING_PROCESSING.format(self.id) + str(e))
                self.write({"state": "failed", "state_message": str(e)})
                emails = self.failure_emails
                if emails:
                    self.env.ref(
                        "attachment_queue.attachment_failure_notification"
                    ).send_mail(self.id)
                self._additional_error_hook(e)

    def _additional_error_hook(self, e):
        return True

    def run(self):
        """
        Run the process for an individual attachment queue
        """
        self._run()
        self.write(
            {
                "state": "done",
                "date_done": fields.Datetime.now(),
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
