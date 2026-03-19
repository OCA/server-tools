# Copyright 2013-2026 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import api, fields, models
from odoo.fields import Command

_logger = logging.getLogger(__name__)


class AttachMailManually(models.TransientModel):
    """Attach mail to selected documents."""

    _name = "fetchmail.attach.mail.manually"
    _description = __doc__

    name = fields.Char()
    folder_id = fields.Many2one(comodel_name="fetchmail.server.folder")
    mail_ids = fields.One2many(
        "fetchmail.attach.mail.manually.mail", "wizard_id", "Emails"
    )

    @api.model
    def _prepare_mail(self, folder, message_uid, message_dict):
        return {
            "message_uid": message_uid,
            "subject": message_dict.get("subject", ""),
            "date": message_dict.get("date") or False,
            "body": message_dict.get("body", ""),
            "email_from": message_dict.get("from", ""),
        }

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if not fields_list or "name" in fields_list:
            defaults["name"] = self.env._("Attach emails manually")
        defaults["mail_ids"] = []
        FetchmailServerFolder = self.env["fetchmail.server.folder"]
        folder_id = self.env.context.get("folder_id")
        defaults["folder_id"] = folder_id
        folder = FetchmailServerFolder.browse([folder_id])
        connection = folder.server_id._connect__()
        connection.select(folder.path)
        criteria = "FLAGGED" if folder.flag_nonmatching else folder.get_criteria()
        message_uids = folder.get_message_uids(connection, criteria)
        for message_uid in message_uids[0].split():
            message_org = folder.fetch_msg(connection, message_uid)
            message_dict = folder._get_message_dict(message_org)
            defaults["mail_ids"].append(
                Command.create(self._prepare_mail(folder, message_uid, message_dict))
            )
        connection.close()
        return defaults

    def attach_mails(self):
        self.ensure_one()
        folder = self.folder_id
        server = folder.server_id
        connection = server._connect__()
        connection.select(folder.path)
        for mail in self.mail_ids:
            if not mail.object_id:
                continue
            message_uid = mail.message_uid
            message_org = folder.fetch_msg(connection, message_uid)
            message_dict = folder._get_message_dict(message_org)
            folder.attach_mail(mail.object_id, message_dict)
            folder.update_msg(
                connection, message_uid, matched=True, flagged=folder.flag_nonmatching
            )
        connection.close()
        return {"type": "ir.actions.act_window_close"}


class AttachMailManuallyMail(models.TransientModel):
    """Attach single mail to selected documents."""

    _name = "fetchmail.attach.mail.manually.mail"
    _description = __doc__

    wizard_id = fields.Many2one("fetchmail.attach.mail.manually", readonly=True)
    message_uid = fields.Char("Message id")
    subject = fields.Char(readonly=True)
    date = fields.Datetime(readonly=True)
    email_from = fields.Char("From", readonly=True)
    body = fields.Html(readonly=True)
    object_id = fields.Reference(
        selection=lambda self: self._get_model_selection(),
    )

    def _get_model_selection(self):
        """Selection from all models in the system."""
        Model = self.env["ir.model"]
        return [(m.model, m.name) for m in Model.search([("transient", "=", False)])]
