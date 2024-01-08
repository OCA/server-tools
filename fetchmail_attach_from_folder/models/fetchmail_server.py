# Copyright - 2013-2024 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import re

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

list_response_pattern = re.compile(
    r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)'
)


class FetchmailServer(models.Model):
    _inherit = "fetchmail.server"

    def _compute_folders_available(self):
        """Retrieve available folders from IMAP server."""

        def parse_list_response(line):
            flags, delimiter, mailbox_name = list_response_pattern.match(line).groups()
            mailbox_name = mailbox_name.strip('"')
            return (flags, delimiter, mailbox_name)

        for this in self:
            if this.state != "done":
                this.folders_available = _("Confirm connection first.")
                continue
            connection = this.connect()
            list_result = connection.list()
            if list_result[0] != "OK":
                this.folders_available = _("Unable to retrieve folders.")
                continue
            folders_available = []
            for folder_entry in list_result[1]:
                folders_available.append(parse_list_response(str(folder_entry))[2])
            this.folders_available = "\n".join(folders_available)
            connection.logout()

    folders_available = fields.Text(
        string="Available folders", compute="_compute_folders_available", readonly=True
    )
    folder_ids = fields.One2many(
        comodel_name="fetchmail.server.folder",
        inverse_name="server_id",
        string="Folders",
        context={"active_test": False},
    )
    object_id = fields.Many2one(required=False)  # comodel_name='ir.model'
    server_type = fields.Selection(default="imap")
    folders_only = fields.Boolean(
        string="Only folders, not inbox",
        help="Check this field to leave imap inbox alone"
        " and only retrieve mail from configured folders.",
    )

    @api.onchange("server_type", "is_ssl", "object_id")
    def onchange_server_type(self):
        result = super().onchange_server_type()
        self.state = "draft"
        return result

    def fetch_mail(self):
        result = True
        for this in self:
            if not this.folders_only:
                result = result and super(FetchmailServer, this).fetch_mail()
            this.folder_ids.fetch_mail()
        return result
