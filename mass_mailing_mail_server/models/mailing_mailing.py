# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MailingMailing(models.Model):

    _inherit = "mailing.mailing"

    def action_send_mail(self, res_ids=None):
        """
        If the mail server was chosen on the mass mailing, we use it.
        Otherwise, we look for the best fitted mail server.
        We compute how many recipients will receive the email and then
        search for mail servers having, as minimum number of recipients,
        a value less than (or equal to) the number of recipients.
        """
        mailings_without_server = self.filtered(lambda m: not m.mail_server_id)
        for mailing in mailings_without_server:
            number_recipients = len(mailing._get_remaining_recipients())
            server = self.env["ir.mail_server"].search(
                [("recipients_min", "<=", number_recipients)], limit=1
            )
            mailing.mail_server_id = server

        res = super().action_send_mail(res_ids)

        # Remove the mail server now that the mails were sent
        mailings_without_server.write({"mail_server_id": False})
        return res
