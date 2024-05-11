# Copyright - 2013-2024 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import _, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class FetchmailServerFolder(models.Model):
    """Define folders (IMAP mailboxes) from which to fetch mail."""

    _name = "fetchmail.server.folder"
    _description = __doc__
    _rec_name = "path"
    _order = "sequence"

    server_id = fields.Many2one("fetchmail.server")
    sequence = fields.Integer()
    state = fields.Selection(
        [("draft", "Not Confirmed"), ("done", "Confirmed")],
        string="Status",
        readonly=True,
        required=True,
        copy=False,
        default="draft",
    )
    path = fields.Char(
        required=True,
        help="The path to your mail folder."
        " Typically would be something like 'INBOX.myfolder'",
    )
    archive_path = fields.Char(
        help="The path where successfully retrieved messages will be stored.",
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        required=True,
        ondelete="cascade",
        help="The model to attach emails to",
    )
    model_field = fields.Char(
        "Field (model)",
        help="The field in your model that contains the field to match against.\n"
        "Examples:\n"
        "'email' if your model is res.partner, or "
        "'partner_id.email' if you're matching sale orders",
    )
    model_order = fields.Char(
        "Order (model)",
        help="Field(s) to order by, this mostly useful in conjunction "
        "with 'Use 1st match'",
    )
    match_algorithm = fields.Selection(
        selection=[
            ("odoo_standard", "Odoo standard"),
            ("email_domain", "Domain of email address"),
            ("email_exact", "Exact mailadress"),
        ],
        required=True,
        help="The algorithm used to determine which object an email matches.",
    )
    mail_field = fields.Char(
        "Field (email)",
        help="The field in the email used for matching."
        " Typically this is 'to' or 'from'",
    )
    delete_matching = fields.Boolean(
        "Delete matches", help="Delete matched emails from server"
    )
    flag_nonmatching = fields.Boolean(
        default=True,
        help="Flag emails in the server that don't match any object in Odoo",
    )
    match_first = fields.Boolean(
        "Use 1st match",
        help="If there are multiple matches, use the first one. If "
        "not checked, multiple matches count as no match at all",
    )
    domain = fields.Char(help="Fill in a search filter to narrow down objects to match")
    msg_state = fields.Selection(
        selection=[("sent", "Sent"), ("received", "Received")],
        string="Message state",
        default="received",
        help="The state messages fetched from this folder should be assigned in Odoo",
    )
    active = fields.Boolean(default=True)

    def button_confirm_folder(self):
        self.write({"state": "draft"})
        for this in self:
            if not this.active:
                continue
            connection = this.server_id.connect()
            connection.select()
            if connection.select(this.path)[0] != "OK":
                raise ValidationError(_("Invalid folder %s!") % this.path)
            connection.close()
            this.write({"state": "done"})

    def button_attach_mail_manually(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "fetchmail.attach.mail.manually",
            "target": "new",
            "context": dict(self.env.context, folder_id=self.id),
            "view_type": "form",
            "view_mode": "form",
        }

    def set_draft(self):
        self.write({"state": "draft"})
        return True

    def fetch_mail(self):
        """Retrieve all mails for IMAP folders.

        We will use a separate connection for each folder.
        """
        for this in self:
            if not this.active or this.state != "done":
                continue
            connection = None
            try:
                # New connection per folder
                connection = this.server_id.connect()
                this.check_imap_archive_folder(connection)
                this.retrieve_imap_folder(connection)
                connection.close()
            except Exception:
                _logger.error(
                    (
                        "General failure when trying to connect to"
                        " %(server_type)s server %(server)s."
                    ),
                    {
                        "server_type": this.server_id.server_type,
                        "server": this.server_id.name,
                    },
                    exc_info=True,
                )
            finally:
                if connection:
                    connection.logout()

    def check_imap_archive_folder(self, connection):
        """If archive folder specified, check existance and create when needed."""
        self.ensure_one()
        server = self.server_id
        if not self.archive_path:
            return
        if connection.select(self.archive_path)[0] != "OK":
            connection.create(self.archive_path)
            if connection.select(self.archive_path)[0] != "OK":
                raise UserError(
                    _("Could not create archive folder %(folder)s on server %(server)s")
                    % {"folder": self.archive_path, "server": server.name}
                )

    def retrieve_imap_folder(self, connection):
        """Retrieve all mails for one IMAP folder."""
        self.ensure_one()
        msgids = self.get_msgids(connection, "UNDELETED")
        for msgid in msgids[0].split():
            # We will accept exceptions for single messages
            try:
                self.env.cr.execute("savepoint apply_matching")
                self.apply_matching(connection, msgid)
                self.env.cr.execute("release savepoint apply_matching")
            except Exception:
                self.env.cr.execute("rollback to savepoint apply_matching")
                _logger.exception(
                    "Failed to fetch mail %(msgid)s from server %(server)s",
                    {"msgid": msgid, "server": self.server_id.name},
                )

    def get_msgids(self, connection, criteria):
        """Return imap ids of messages to process"""
        self.ensure_one()
        server = self.server_id
        _logger.info(
            "start checking for emails in folder %(folder)s on server %(server)s",
            {"folder": self.path, "server": server.name},
        )
        if connection.select(self.path)[0] != "OK":
            raise UserError(
                _("Could not open folder %(folder)s on server %(server)s")
                % {"folder": self.path, "server": server.name}
            )
        result, msgids = connection.search(None, criteria)
        if result != "OK":
            raise UserError(
                _("Could not search folder %(folder)s on server %(server)s")
                % {"folder": self.path, "server": server.name}
            )
        _logger.info(
            "finished checking for emails in folder %(folder)s on server %(server)s",
            {"folder": self.path, "server": server.name},
        )
        return msgids

    def apply_matching(self, connection, msgid):
        """Return id of object matched (which will be the thread_id)."""
        self.ensure_one()
        thread_model = self.env["mail.thread"]
        message_org = self.fetch_msg(connection, msgid)
        custom_values = (
            None
            if self.match_algorithm == "odoo_standard"
            else {
                "folder": self,
            }
        )
        thread_id = thread_model.message_process(
            self.model_id.model,
            message_org,
            custom_values=custom_values,
            save_original=self.server_id.original,
            strip_attachments=(not self.server_id.attach),
        )
        matched = True if thread_id else False
        self.update_msg(connection, msgid, matched=matched)
        if self.archive_path:
            self._archive_msg(connection, msgid)
        return thread_id  # Can be None if no match found.

    def fetch_msg(self, connection, msgid):
        """Select a single message from a folder."""
        self.ensure_one()
        result, msgdata = connection.fetch(msgid, "(RFC822)")
        if result != "OK":
            raise UserError(
                _("Could not fetch %(msgid)s in folder %(folder)s on server %(server)s")
                % {"msgid": msgid, "folder": self.path, "server": self.server_id.name}
            )
        message_org = msgdata[0][1]  # rfc822 message source
        return message_org

    def update_msg(self, connection, msgid, matched=True, flagged=False):
        """Update msg in imap folder depending on match and settings."""
        if matched:
            if self.delete_matching:
                connection.store(msgid, "+FLAGS", "\\DELETED")
            elif flagged and self.flag_nonmatching:
                connection.store(msgid, "-FLAGS", "\\FLAGGED")
        else:
            if self.flag_nonmatching:
                connection.store(msgid, "+FLAGS", "\\FLAGGED")

    def _archive_msg(self, connection, msgid):
        """Archive message. Folder should already have been created."""
        self.ensure_one()
        connection.copy(msgid, self.archive_path)
        connection.store(msgid, "+FLAGS", "\\Deleted")
        connection.expunge()
