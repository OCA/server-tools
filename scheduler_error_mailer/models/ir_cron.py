# © 2012-2013 Akretion Sébastien BEAU,David Beal,Alexis de Lattre
# © 2016 Sodexis
# © 2018 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
import logging
import traceback


_logger = logging.getLogger(__name__)


class IrCron(models.Model):
    _inherit = "ir.cron"

    email_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Error E-mail Template",
        help="Select the email template that will be sent when "
        "this scheduler fails."
    )

    show_error_trace = fields.Boolean(
        string="Show error trace",
        help="Check this if you want to show in the error message mail the "
             "error trace.")

    @api.model
    def _handle_callback_exception(self, cron_name, server_action_id, job_id,
                                   job_exception):
        res = super(IrCron, self)._handle_callback_exception(cron_name,
                                                             server_action_id,
                                                             job_id,
                                                             job_exception)
        my_cron = self.browse(job_id)

        if my_cron.email_template_id:

            # we put the job_exception in context to be able to print it inside
            # the email template
            context = {
                'job_exception': job_exception,
                'dbname': self._cr.dbname,
            }

            if my_cron.show_error_trace:
                trace = traceback.format_exc()
                context.update({
                    "trace_exception": trace.split("\n") if trace else ""})

            _logger.debug(
                "Sending scheduler error email with context=%s", context)

            self.env['mail.template'].browse(
                my_cron.email_template_id.id
            ).with_context(context).sudo().send_mail(
                my_cron.id, force_send=True)

        return res

    @api.model
    def _test_scheduler_failure(self):
        """This function is used to test and debug this module."""
        raise UserError(
            _("Task failure with UID = %d.") % self._uid)
