# Copyright 2012-2013 Akretion Sébastien BEAU,David Beal,Alexis de Lattre
# Copyright 2016 Sodexis
# Copyright 2018 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models
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

    def _handle_callback_exception(self, cron_name, server_action_id, job_exception):
        self.ensure_one()
        if self.email_template_id:
            # we put the job_exception in context to be able to print it inside
            # the email template
            context = {"job_exception": str(job_exception), "dbname": self._cr.dbname}

            _logger.debug("Sending scheduler error email with context=%s", context)

            template = self.email_template_id.with_context(**context).sudo()
            template.send_mail(self.id, force_send=True)

    @api.model
    def _test_scheduler_failure(self):
        """This function is used to test and debug this module."""
        raise UserError(self.env._("Task failure with UID = %(uid)d.", uid=self._uid))

    @api.model
    def _callback(self, cron_name, server_action_id):
        try:
            return super()._callback(cron_name, server_action_id)
        except Exception as e:
            self._handle_callback_exception(cron_name, server_action_id, e)

            # Re-raise the original job exception
            raise
