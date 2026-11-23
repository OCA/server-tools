# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models

from odoo.addons.queue_job.job import CANCELLED, FAILED


class QueueJob(models.Model):
    _inherit = "queue.job"

    def _attachment_queues(self):
        """Return the attachment queues processed by the job (if any)"""
        self.ensure_one()
        if self.model_name != "attachment.queue" or self.method_name != "run_as_job":
            return self.env["attachment.queue"]
        return self.records.sudo().exists().filtered(lambda att: att.state != "done")

    def write(self, vals):
        res = super().write(vals)
        # The attachment is not flagged as failed by the job itself (a retryable
        # error would report a failure that is going to be retried): report it only
        # when the job is definitively failed.
        # This must be done after the write: queue.job calls
        # '_message_post_on_failure' before writing the values, so exc_message is
        # not yet stored on the job at that time.
        if vals.get("state") == FAILED:
            for job in self:
                attachments = job._attachment_queues()
                if attachments:
                    attachments._set_attachment_failure(job.exc_message or job.exc_name)
        return res

    def _change_job_state(self, state, result=None):
        res = super()._change_job_state(state, result=result)
        if state == CANCELLED:
            for job in self:
                # No job is left to process the attachment nor to report a failure:
                # the attachment would stay pending forever.
                attachments = job._attachment_queues()
                if attachments:
                    attachments.write(
                        {"state": "failed", "state_message": _("Job cancelled")}
                    )
        return res
