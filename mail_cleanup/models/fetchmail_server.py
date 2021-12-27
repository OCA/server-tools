# Copyright 2015-2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime
import logging

from dateutil.relativedelta import relativedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class FetchmailServer(models.Model):
    """Incoming POP/IMAP mail server account."""

    _inherit = "fetchmail.server"

    cleanup_days = fields.Integer(
        string="Expiration days",
        help="Number of days before marking an e-mail as read",
    )

    cleanup_folder = fields.Char(
        string="Expiration folder",
        help="Folder where an e-mail marked as read will be moved.",
    )

    purge_days = fields.Integer(
        string="Deletion days",
        help="Number of days before removing an e-mail",
    )

    @property
    def _server_env_fields(self):
        base_fields = super()._server_env_fields
        mail_cleanup_fields = {
            "cleanup_days": {
                "getter": "getint",
            },
            "purge_days": {
                "getter": "getint",
            },
            "cleanup_folder": {},
        }
        mail_cleanup_fields.update(base_fields)
        return mail_cleanup_fields

    def _cleanup_fetchmail_server(self, server, imap_server):
        count, failed = 0, 0
        expiration_date = datetime.date.today()
        expiration_date -= relativedelta(days=server.cleanup_days)
        search_text = expiration_date.strftime("(UNSEEN BEFORE %d-%b-%Y)")
        imap_server.select()
        result, data = imap_server.search(None, search_text)
        for num in data[0].split():
            try:
                # Mark message as read
                imap_server.store(num, "+FLAGS", "\\Seen")
                if server.cleanup_folder:
                    # To move a message, you have to COPY
                    # then DELETE the message
                    result = imap_server.copy(num, server.cleanup_folder)
                    if result[0] == "OK":
                        imap_server.store(num, "+FLAGS", "\\Deleted")
            except Exception:
                _logger.exception(
                    "Failed to cleanup mail from %s server %s.",
                    server.server_type,
                    server.name,
                )
                failed += 1
            count += 1
        _logger.info(
            "Marked %d email(s) as read on %s server %s;" " %d succeeded, %d failed.",
            count,
            server.server_type,
            server.name,
            (count - failed),
            failed,
        )

    def _purge_fetchmail_server(self, server, imap_server):
        # Purging e-mails older than the purge date, if available
        count, failed = 0, 0
        purge_date = datetime.date.today()
        purge_date -= relativedelta(days=server.purge_days)
        search_text = purge_date.strftime("(BEFORE %d-%b-%Y)")
        imap_server.select()
        result, data = imap_server.search(None, search_text)
        for num in data[0].split():
            try:
                # Delete message
                imap_server.store(num, "+FLAGS", "\\Deleted")
            except Exception:
                _logger.exception(
                    "Failed to remove mail from %s server %s.",
                    server.server_type,
                    server.name,
                )
                failed += 1
            count += 1
        _logger.info(
            "Removed %d email(s) on %s server %s;" " %d succeeded, %d failed.",
            count,
            server.server_type,
            server.name,
            (count - failed),
            failed,
        )

    def fetch_mail(self):
        # Called before the fetch, in order to clean up right before
        # retrieving emails.
        for server in self:
            _logger.info(
                "start cleaning up emails on %s server %s",
                server.server_type,
                server.name,
            )
            imap_server = False
            if server.server_type == "imap":
                try:
                    imap_server = server.connect()
                    if server.cleanup_days > 0:
                        self._cleanup_fetchmail_server(server, imap_server)
                    if server.purge_days > 0:
                        self._purge_fetchmail_server(server, imap_server)
                    # Do the final cleanup: delete all messages
                    # flagged as deleted
                    imap_server.expunge()
                except Exception:
                    _logger.exception(
                        "General failure when trying to cleanup"
                        " mail from %s server %s.",
                        server.server_type,
                        server.name,
                    )
                finally:
                    if imap_server:
                        imap_server.close()
                        imap_server.logout()
        return super().fetch_mail()
