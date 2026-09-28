# Copyright - 2013-2026 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import email
import email.policy
import logging
from xmlrpc import client as xmlrpclib

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.mail import decode_message_header, email_split_and_format

from .. import match_algorithm

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
        string="Fetch from Folder",
        help="Specify the IMAP folder path to retrieve emails from. "
        "Typically, this would be something like 'INBOX.myfolder'.",
    )
    archive_path = fields.Char(
        string="Archive Folder",
        help="Specify the folder where successfully retrieved emails will be moved "
        "after processing. If left empty, emails will remain in the original folder.",
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        required=True,
        ondelete="cascade",
        string="Target Model",
        help="The model to attach emails to",
    )
    model_field = fields.Char(
        help="Specify the field in the model that will be used for email matching.\n"
        "Examples:\n"
        "- 'email' if your model is res.partner\n"
        "- 'partner_id.email' if matching sale orders.",
    )
    model_order = fields.Char(
        help="Specify the field(s) to order by when matching emails. "
        "This is mostly useful in conjunction with 'Use 1st Match'.",
    )
    match_algorithm = fields.Selection(
        selection=[
            ("odoo_standard", "Odoo Standard"),
            ("email_domain", "Domain of Email Address"),
            ("email_exact", "Exact Email Address"),
        ],
        required=True,
        string="Matching Algorithm",
        help="Select the algorithm used to determine which object an email matches.",
    )
    mail_field = fields.Char(
        string="Email Field",
        help="Specify the field in the email used for matching. "
        "Typically, this is 'to', 'from' or 'reply_to'.",
    )
    delete_matching = fields.Boolean(
        string="Delete Matched Emails",
        help="Enable this option to delete emails after they are successfully "
        "processed and matched.",
    )
    flag_nonmatching = fields.Boolean(
        string="Flag Non-Matching Emails",
        default=True,
        help="Enable this option to mark emails as important if they do not match "
        "any object in Odoo.",
    )
    match_first = fields.Boolean(
        string="Use First Match",
        help="If there are multiple matches, use the first one. "
        "If disabled, multiple matches will be considered as no match.",
    )
    domain = fields.Char(
        string="Matching Domain",
        help="Define a search filter to narrow down objects for email matching.",
    )
    msg_state = fields.Selection(
        selection=[("sent", "Sent"), ("received", "Received")],
        string="Message state",
        default="received",
        help="The state messages fetched from this folder should be assigned in Odoo",
    )
    active = fields.Boolean(default=True)
    action_id = fields.Many2one(
        comodel_name="ir.actions.server",
        string="Server Action",
        help="Specify an optional custom server action to trigger for each incoming"
        " email. The action will run on the record that was created or updated by"
        " this email.",
    )
    fetch_unseen_only = fields.Boolean(
        help="By default, all undeleted emails are retrieved. "
        "Enable this option to fetch only unread emails.",
    )
    fetch_last_day_only = fields.Boolean(
        string="Fetch Last 24 Hours Only",
        help="By default, all emails in the folder are searched. Enable this "
        "option to only fetch emails received in the last 24 hours. This helps "
        "avoid reprocessing emails if they are not deleted after processing.",
    )
    seen = fields.Selection(
        selection=[
            ("on_fetch", "Immediately on Fetch"),
            ("all", "After Processing"),
            ("matching", "When matching"),
            ("none", "Never"),
        ],
        string="Mark email as seen",
        required=True,
        default="on_fetch",
    )

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

    def get_criteria(self):
        criteria = "UNSEEN UNDELETED" if self.fetch_unseen_only else "UNDELETED"
        if self.fetch_last_day_only:
            yesterday = fields.Date.subtract(
                fields.Date.context_today(self), days=1
            ).strftime("%d-%b-%Y")
            criteria = f"SINCE {yesterday} {criteria}"
        return criteria

    def retrieve_imap_folder(self, connection):
        """Retrieve all mails for one IMAP folder."""
        self.ensure_one()
        message_uids = self.get_message_uids(connection, self.get_criteria())
        for message_uid in message_uids[0].split():
            # We will accept exceptions for single messages
            try:
                self.env.cr.execute("savepoint apply_matching")
                self.apply_matching(connection, message_uid)
                self.env.cr.execute("release savepoint apply_matching")
            except Exception:
                self.env.cr.execute("rollback to savepoint apply_matching")
                _logger.exception(
                    "Failed to fetch mail %(message_uid)s from server %(server)s",
                    {"message_uid": message_uid, "server": self.server_id.name},
                )

    def get_message_uids(self, connection, criteria):
        """Return imap ids of messages to process"""
        # Note that these message_uids are linked to the folder on
        # the imap server. They have nothing at all todo with the
        # message_id field that is part of the message itself, and the
        # two should not be confused.
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
        charset = None  # Generally we do not need to set a charset.
        result, message_uids = connection.uid("search", charset, criteria)
        if result != "OK":
            raise UserError(
                _("Could not search folder %(folder)s on server %(server)s")
                % {"folder": self.path, "server": server.name}
            )
        _logger.info(
            "finished checking for emails in folder %(folder)s on server %(server)s",
            {"folder": self.path, "server": server.name},
        )
        return message_uids

    def apply_matching(self, connection, message_uid):
        """Return id of object matched (which will be the thread_id)."""
        self.ensure_one()
        thread_id = None
        thread_model = self.env["mail.thread"]
        message_org = self.fetch_msg(connection, message_uid)
        if self.match_algorithm == "odoo_standard":
            thread_id = thread_model.message_process(
                self.model_id.model,
                message_org,
                save_original=self.server_id.original,
                strip_attachments=(not self.server_id.attach),
            )
        else:
            message_dict = self._get_message_dict(message_org)
            if not self._check_message_already_present(message_dict):
                match = self._find_match(message_dict)
                if match:
                    thread_id = match.id
                    self.attach_mail(match, message_dict)
        matched = True if thread_id else False
        if matched:
            self.run_server_action(thread_id)
        self.update_msg(connection, message_uid, matched=matched)
        if self.archive_path and not self.delete_matching:
            self._archive_msg(connection, message_uid)
        return thread_id  # Can be None if no match found.

    def run_server_action(self, matched_object_ids):
        action = self.action_id
        if not action:
            return
        records = self.env[self.model_id.model].browse(matched_object_ids)
        for record in records:
            if not record.exists():
                continue
            action.with_context(
                **{
                    "active_id": record.id,
                    "active_ids": record.ids,
                    "active_model": self.model_id.model,
                }
            ).run()

    def fetch_msg(self, connection, message_uid):
        """Select a single message from a folder."""
        self.ensure_one()
        command = "(RFC822)" if self.seen == "on_fetch" else "(BODY.PEEK[])"
        result, msgdata = connection.uid("fetch", message_uid, command)
        if result != "OK":
            raise UserError(
                _(
                    "Could not fetch %(message_uid)s in folder %(folder)s"
                    " on server %(server)s",
                    message_uid=message_uid,
                    folder=self.path,
                    server=self.server_id.name,
                )
            )
        message_org = msgdata[0][1]  # rfc822 message source
        return message_org

    def update_msg(self, connection, message_uid, matched=True, flagged=False):
        """Update msg in imap folder depending on match and settings."""
        if self.seen == "all" or (matched and self.seen == "matching"):
            connection.uid("store", message_uid, "+FLAGS", "\\Seen")
        if matched:
            if self.delete_matching:
                connection.uid("store", message_uid, "+FLAGS", "\\DELETED")
            elif flagged and self.flag_nonmatching:
                connection.uid("store", message_uid, "-FLAGS", "\\FLAGGED")
        else:
            if self.flag_nonmatching:
                connection.uid("store", message_uid, "+FLAGS", "\\FLAGGED")

    def _archive_msg(self, connection, message_uid):
        """Archive message. Folder should already have been created."""
        connection.uid("copy", message_uid, self.archive_path)
        connection.uid("store", message_uid, "+FLAGS", "\\Deleted")
        connection.expunge()

    @api.model
    def _get_message_dict(self, message):
        """Get message_dict from original message.

        This uses some code copied from mail.thread.message_process, that
        unfortunately is not in a separate method.
        """
        if isinstance(message, xmlrpclib.Binary):
            message = bytes(message.data)
        if isinstance(message, str):
            message = message.encode("utf-8")
        message = email.message_from_bytes(message, policy=email.policy.SMTP)
        thread_model = self.env["mail.thread"]
        message_dict = thread_model.message_parse(
            message, save_original=self.server_id.original
        )
        # Populate `reply_to`
        message_dict["reply_to"] = ",".join(
            {
                formatted_email
                for address in [
                    decode_message_header(message, "Reply-To", separator=","),
                ]
                if address
                for formatted_email in email_split_and_format(address)
            }
        )
        return message_dict

    def _check_message_already_present(self, message_dict):
        """If message already handled, it should be ignored."""
        message_id = message_dict["message_id"]
        if self.env["mail.message"].search([("message_id", "=", message_id)], limit=1):
            _logger.debug(
                "Message %(message_id)s already in database",
                {"message_id": message_id},
            )
            return True
        return False

    def _find_match(self, message_dict):
        """Try to find existing object to link mail to."""
        self.ensure_one()
        matcher = self._get_algorithm()
        if not matcher:
            return None
        matches = matcher.search_matches(self, message_dict)
        if not matches:
            _logger.info(
                "No match found for message %(subject)s"
                " with message_uid %(message_uid)s -"
                " To: %(to)s - From: %(from)s - Reply-To: %(reply_to)s",
                {
                    "subject": message_dict.get("subject", "no subject"),
                    "message_uid": message_dict.get("message_id", "no message_uid"),
                    "to": message_dict.get("to", ""),
                    "from": message_dict.get("from", ""),
                    "reply_to": message_dict.get("reply_to", ""),
                },
            )
            return None
        if len(matches) > 1:
            _logger.debug(
                "Multiple matches found: %(matches)s",
                {
                    "matches": ", ".join(
                        [str((match.id, match.display_name)) for match in matches]
                    ),
                },
            )
        matched = len(matches) == 1 or self.match_first
        return matched and matches[0] or None

    def _get_algorithm(self):
        """Translate algorithm code to implementation class.

        We used to load this dynamically, but having it more or less hardcoded
        allows to adapt the UI to the selected algorithm, withouth needing
        the (deprecated) fields_view_get trickery we used in the past.
        """
        self.ensure_one()
        if self.match_algorithm == "email_domain":
            return match_algorithm.email_domain.EmailDomain()
        if self.match_algorithm == "email_exact":
            return match_algorithm.email_exact.EmailExact()
        _logger.error(
            "Unknown algorithm %(algorithm)s", {"algorithm": self.match_algorithm}
        )
        return None

    def attach_mail(self, match_object, message_dict):
        """Attach mail to match_object."""
        self.ensure_one()
        partner = False
        model_name = self.model_id.model
        if model_name == "res.partner":
            partner = match_object
        elif "partner_id" in self.env[model_name]._fields:
            partner = match_object.partner_id
        message_model = self.env["mail.message"]
        msg_values = {
            key: val
            for key, val in message_dict.items()
            if key in message_model._fields
        }
        msg_values.update(
            {
                "author_id": partner and partner.id or False,
                "model": model_name,
                "res_id": match_object.id,
                "message_type": "email",
            }
        )
        thread_model = self.env["mail.thread"]
        attachments = message_dict["attachments"] or []
        attachment_ids = []
        attachement_values = thread_model._process_attachments_for_post(
            attachments, attachment_ids, msg_values
        )
        msg_values.update(attachement_values)
        message = message_model.create(msg_values)
        _logger.debug(
            "Message with id %(message_id)s created"
            " for %(model_name)s with id %(thread_id)s",
            {
                "message_id": message.id,
                "model_name": model_name,
                "thread_id": match_object.id,
            },
        )
