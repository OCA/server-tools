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
        string="Error E-mail Template",
        help="Select the email template that will be sent when "
        "this scheduler fails.",
    )

    @api.model
    def _handle_callback_exception(
        self, cron_name, server_action_id, job_id, job_exception
    ):
        super()._handle_callback_exception(
            cron_name, server_action_id, job_id, job_exception
        )
        my_cron = self.browse(job_id)

        if my_cron.email_template_id:
            # we put the job_exception in context to be able to print it inside
            # the email template
            context = {
                "job_exception": job_exception,
                "dbname": self._cr.dbname,
            }

            _logger.debug("Sending scheduler error email with context=%s", context)

            self.env["mail.template"].browse(my_cron.email_template_id.id).with_context(
                context
            ).sudo().send_mail(my_cron.id, force_send=True)

    @api.model
    def _test_scheduler_failure(self):
        """This function is used to test and debug this module."""
        raise UserError(_("Task failure with UID = %d.") % self._uid)
