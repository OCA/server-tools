# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from datetime import date

from odoo import api, models
from odoo.exceptions import UserError
from odoo.tools import formataddr

_logger = logging.getLogger(__name__)


class MailMail(models.Model):
    """Override mail.mail to use internal email as sender and reply-to"""

    _inherit = "mail.mail"

    def _get_user_internal_email(self, author_id=None):
        """Get user's internal email from mail_server_manager.

        Args:
            author_id: Partner ID of the author (optional)

        Returns:
            tuple: (user record, internal_email) or (None, None)
        """
        user = None

        if author_id:
            # Find user by partner_id
            user = (
                self.env["res.users"]
                .sudo()
                .search([("partner_id", "=", author_id)], limit=1)
            )

        # Only use env.user if we're in a real user session
        if not user and author_id is None:
            current_user = self.env.user
            if (
                current_user.id not in (1, False)
                and current_user.partner_id
                and current_user.internal_email
            ):
                user = current_user

        if user and user.internal_email:
            return user, user.internal_email
        return None, None

    @api.model_create_multi
    def create(self, vals_list):
        """Override to use internal email as sender and reply-to.

        When creating an outgoing email, if the author (user) has an
        internal email configured via mail_server_manager:
        - Use it as email_from
        - Set reply_to to the internal email so replies come back correctly
        """
        for vals in vals_list:
            user, internal_email = self._get_user_internal_email(vals.get("author_id"))

            if user and internal_email:
                name = user.name or internal_email.split("@")[0]
                formatted_email = formataddr((name, internal_email))

                # Set email_from to internal email
                if vals.get("email_from") != formatted_email:
                    _logger.debug(
                        "Setting email_from to internal email '%s' for user %s",
                        internal_email,
                        user.login,
                    )
                    vals["email_from"] = formatted_email

                # Set reply_to to internal email if not already set
                if not vals.get("reply_to"):
                    vals["reply_to"] = formatted_email
                    _logger.debug(
                        "Setting reply_to to internal email '%s' for user %s",
                        internal_email,
                        user.login,
                    )

        return super().create(vals_list)

    def _send_prepare_values(self, partner=None):
        """Override to ensure reply_to uses internal email.

        This method is called when preparing email values for sending.
        We ensure the reply_to header is set to the user's internal email.
        """
        res = super()._send_prepare_values(partner=partner)

        # If reply_to not set, try to use internal email
        if not res.get("reply_to"):
            user, internal_email = self._get_user_internal_email(
                self.author_id.id if self.author_id else None
            )
            if internal_email:
                name = user.name if user else ""
                res["reply_to"] = formataddr((name, internal_email))

        return res

    def _check_email_limit(self, mail_account):
        """Check if user has reached their daily email limit.

        Returns True if sending is allowed, raises UserError if limit exceeded.
        """
        if not mail_account:
            return True

        today = date.today()

        # Reset counter if it's a new day
        if mail_account.last_email_count_reset != today:
            mail_account.sudo().write(
                {
                    "emails_sent_today": 0,
                    "last_email_count_reset": today,
                }
            )

        # Get effective limit (account-specific or system default)
        limit = mail_account.daily_email_limit
        if limit == 0:
            # Use system default
            ICP = self.env["ir.config_parameter"].sudo()
            limit = int(ICP.get_param("mail_server_manager.daily_email_limit", 100))

        # 0 means unlimited
        if limit == 0:
            return True

        if mail_account.emails_sent_today >= limit:
            raise UserError(
                self.env._(
                    "Daily email limit reached. "
                    "Please try again tomorrow or contact your administrator."
                )
            )

        return True

    def _increment_email_counter(self, mail_account):
        """Increment the email sent counter for the mail account."""
        if mail_account:
            mail_account.sudo().write(
                {
                    "emails_sent_today": mail_account.emails_sent_today + 1,
                    "last_email_count_reset": date.today(),
                }
            )

    def send(self, auto_commit=False, raise_exception=False):
        """Override send to check email limits before sending."""
        for mail in self:
            # Find the user's mail account
            user, internal_email = mail._get_user_internal_email(
                mail.author_id.id if mail.author_id else None
            )
            if user and user.mail_account_id:
                mail._check_email_limit(user.mail_account_id)

        result = super().send(auto_commit=auto_commit, raise_exception=raise_exception)

        # Increment counters for successfully sent emails
        for mail in self.filtered(lambda m: m.state == "sent"):
            user, internal_email = mail._get_user_internal_email(
                mail.author_id.id if mail.author_id else None
            )
            if user and user.mail_account_id:
                mail._increment_email_counter(user.mail_account_id)

        return result
