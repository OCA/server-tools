# Copyright 2013-2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class AttachMailManually(models.TransientModel):
    """Attach mail to selected documents."""

    _name = "fetchmail.attach.mail.manually"
    _description = __doc__

    name = fields.Char()
    folder_id = fields.Many2one(comodel_name="fetchmail.server.folder", readonly=True)
    mail_ids = fields.One2many(
        "fetchmail.attach.mail.manually.mail", "wizard_id", "Emails"
    )

    @api.model
    def _prepare_mail(self, folder, msgid, mail_message):
        return {
            "msgid": msgid,
            "subject": mail_message.get("subject", ""),
            "date": mail_message.get("date", ""),
            "body": mail_message.get("body", ""),
            "email_from": mail_message.get("from", ""),
            "object_id": "%s,-1" % folder.model_id.model,
        }

    @api.model
    def default_get(self, fields_list):
        defaults = super(AttachMailManually, self).default_get(fields_list)
        if not fields_list or "name" in fields_list:
            defaults["name"] = _("Attach emails manually")
        defaults["mail_ids"] = []
        folder_model = self.env["fetchmail.server.folder"]
        folder_id = self.env.context.get("folder_id")
        defaults["folder_id"] = folder_id
        folder = folder_model.browse([folder_id])
        connection = folder.server_id.connect()
        connection.select(folder.path)
        criteria = "FLAGGED" if folder.flag_nonmatching else folder.get_criteria()
        msgids = folder.get_msgids(connection, criteria)
        for msgid in msgids[0].split():
            mail_message, message_org = folder.fetch_msg(connection, msgid)
            defaults["mail_ids"].append(
                (0, 0, self._prepare_mail(folder, msgid, mail_message))
            )
        connection.close()
        return defaults

    def attach_mails(self):
        self.ensure_one()
        folder = self.folder_id
        server = folder.server_id
        connection = server.connect()
        connection.select(folder.path)
        for mail in self.mail_ids:
            if not mail.object_id:
                continue
            msgid = mail.msgid
            mail_message, message_org = folder.fetch_msg(connection, msgid)
            folder.attach_mail(mail.object_id, mail_message)
            folder.update_msg(
                connection, msgid, matched=True, flagged=folder.flag_nonmatching
            )
        connection.close()
        return {"type": "ir.actions.act_window_close"}

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        # TODO: Change or replace this...
        result = super(AttachMailManually, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if view_type != "form":
            return result
        folder_model = self.env["fetchmail.server.folder"]
        folder_id = self.env.context.get("folder_id")
        folder = folder_model.browse([folder_id])
        form = result["fields"]["mail_ids"]["views"]["form"]
        form["fields"]["object_id"]["selection"] = [
            (folder.model_id.model, folder.model_id.name)
        ]
        return result


class AttachMailManuallyMail(models.TransientModel):
    """Attach single mail to selected documents."""

    _name = "fetchmail.attach.mail.manually.mail"
    _description = __doc__

    wizard_id = fields.Many2one("fetchmail.attach.mail.manually", readonly=True)
    msgid = fields.Char("Message id", readonly=True)
    subject = fields.Char(readonly=True)
    date = fields.Datetime(readonly=True)
    email_from = fields.Char("From", readonly=True)
    body = fields.Html(readonly=True)
    object_id = fields.Reference(
        lambda self: [(m.model, m.name) for m in self.env["ir.model"].search([])]
    )
