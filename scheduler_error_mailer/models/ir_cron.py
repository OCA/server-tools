# Copyright 2012-2013 Akretion Sébastien BEAU,David Beal,Alexis de Lattre
# Copyright 2016 Sodexis
# Copyright 2018 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IrCron(models.Model):
    _inherit = "ir.cron"

    email_template_id = fields.Many2one(
        comodel_name="mail.template",
        domain=[("model_id.model", "=", "ir.cron")],
        string="Error E-mail Template",
        help="Select the email template that will be sent when "
        "this scheduler fails.",
        default=lambda self: self.env.ref(
            "scheduler_error_mailer.scheduler_error_mailer", False
        ),
    )
    email_retries = fields.Integer(
        default=1,
        help="Number of consecutive failures allowed "
        "before the error email is sent.",
    )

    @api.model
    def _callback(self, cron_name, server_action_id, job_id):
        # failure_count is stored on the delegated ir.actions.server row:
        # the scheduler locks the ir_cron row while the job runs, so the
        # cron record itself cannot be written from within the job
        action = self.env["ir.actions.server"].sudo().browse(server_action_id)
        failures_before = action.failure_count
        res = super()._callback(cron_name, server_action_id, job_id)
        if failures_before and action.failure_count == failures_before:
            action.failure_count = 0
        return res

    @api.model
    def _handle_callback_exception(
        self, cron_name, server_action_id, job_id, job_exception
    ):
        res = super()._handle_callback_exception(
            cron_name, server_action_id, job_id, job_exception
        )
        my_cron = self.browse(job_id)

        if my_cron.email_template_id:
            action = my_cron.ir_actions_server_id.sudo()
            action.failure_count += 1
            if action.failure_count < my_cron.email_retries:
                return res
            action.failure_count = 0

            # we put the job_exception in context to be able to print it inside
            # the email template
            context = {"job_exception": str(job_exception), "dbname": self._cr.dbname}

            _logger.debug("Sending scheduler error email with context=%s", context)

            template = my_cron.email_template_id.with_context(**context).sudo()
            template.send_mail(my_cron.id, force_send=True)

        return res

    @api.model
    def _test_scheduler_failure(self):
        """This function is used to test and debug this module."""
        raise UserError(_("Task failure with UID = %d.") % self._uid)
