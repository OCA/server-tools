# Copyright 2020 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
import re
import smtplib
import sys
import threading
from email.utils import formataddr, parseaddr

from odoo import api, models
from odoo.tools import ustr
from odoo.tools.translate import _

from odoo.addons.base.models.ir_mail_server import (
    MailDeliveryException,
    extract_rfc2822_addresses,
    is_ascii,
)

_logger = logging.getLogger(__name__)
_test_logger = logging.getLogger("odoo.tests")


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    @api.model
    def switch_smtp_from(self, smtp, message):
        """Methods that switch the smtp email from to use where relaying is
        disallowed.

        This method alter the given `message` object and return the smtp email
        to use.

        :param smtp: established SMTP session
        :param message: the email.message.Message to send.
        """
        # exact name and address
        (oldname, oldemail) = parseaddr(message["From"])
        # use original name with new address
        newfrom = formataddr((oldname, smtp.user))
        # need to use replace_header instead '=' to prevent
        # double field
        message.replace_header("From", newfrom)
        return smtp.user

    @api.model
    def send_email(
        self,
        message,
        mail_server_id=None,
        smtp_server=None,
        smtp_port=None,
        smtp_user=None,
        smtp_password=None,
        smtp_encryption=None,
        smtp_debug=False,
        smtp_session=None,
    ):
        """Override the standard method to fix the issue of using a mail
        client where relaying is disallowed."""
        # Use the default bounce address **only if** no Return-Path was
        # provided by caller.  Caller may be using Variable Envelope Return
        # Path (VERP) to detect no-longer valid email addresses.
        smtp_from = (
            message["Return-Path"]
            or self._get_default_bounce_address()
            or message["From"]
        )
        assert (
            smtp_from
        ), "The Return-Path or From header is required for any outbound email"

        # The email's "Envelope From" (Return-Path), and all recipient addresses
        # must only contain ASCII characters.
        from_rfc2822 = extract_rfc2822_addresses(smtp_from)
        assert from_rfc2822, (
            "Malformed 'Return-Path' or 'From' address: %r - "
            "It should contain one valid plain ASCII email"
        ) % smtp_from
        # use last extracted email, to support rarities like
        # 'Support@MyComp <support@mycompany.com>'
        smtp_from = from_rfc2822[-1]
        email_to = message["To"]
        email_cc = message["Cc"]
        email_bcc = message["Bcc"]
        del message["Bcc"]

        smtp_to_list = [
            address
            for base in [email_to, email_cc, email_bcc]
            for address in extract_rfc2822_addresses(base)
            if address
        ]
        assert smtp_to_list, self.NO_VALID_RECIPIENT

        x_forge_to = message["X-Forge-To"]
        if x_forge_to:
            # `To:` header forged, e.g. for posting on mail.channels,
            # to avoid confusion
            del message["X-Forge-To"]
            del message["To"]  # avoid multiple To: headers!
            message["To"] = x_forge_to

        # Do not actually send emails in testing mode!
        if (
            getattr(threading.currentThread(), "testing", False)
            or self.env.registry.in_test_mode()
        ):
            _test_logger.info("skip sending email in test mode")
            return message["Message-Id"]

        try:
            message_id = message["Message-Id"]
            smtp = smtp_session
            smtp = smtp or self.connect(
                smtp_server,
                smtp_port,
                smtp_user,
                smtp_password,
                smtp_encryption,
                smtp_debug,
                mail_server_id=mail_server_id,
            )

            # START OF CODE ADDED
            smtp_from = self.switch_smtp_from(smtp, message)
            # END OF CODE ADDED

            if sys.version_info < (3, 7, 4):
                # header folding code is buggy and adds redundant carriage
                # returns, it got fixed in 3.7.4 thanks to bpo-34424
                message_str = message.as_string()
                message_str = re.sub("\r+(?!\n)", "", message_str)

                mail_options = []
                if any(not is_ascii(addr) for addr in smtp_to_list + [smtp_from]):
                    # non ascii email found, require SMTPUTF8 extension,
                    # the relay may reject it
                    mail_options.append("SMTPUTF8")
                smtp.sendmail(
                    smtp_from, smtp_to_list, message_str, mail_options=mail_options
                )
            else:
                smtp.send_message(message, smtp_from, smtp_to_list)

            # do not quit() a pre-established smtp_session
            if not smtp_session:
                smtp.quit()
        except smtplib.SMTPServerDisconnected:
            raise
        except Exception as e:
            params = (ustr(smtp_server), e.__class__.__name__, ustr(e))
            msg = _("Mail delivery failed via SMTP server '%s'.\n%s: %s", *params)
            _logger.info(msg)
            raise MailDeliveryException(_("Mail Delivery Failed"), msg)
        return message_id
