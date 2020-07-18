# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class FetchmailServer(models.Model):
    _inherit = "fetchmail.server"

    def company_default_get(self):
        company_id = self.env["res.company"]._company_default_get("fetchmail.server")
        return self.env["res.company"].browse(company_id).id

    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=company_default_get
    )
    attachment_condition_ids = fields.One2many(
        "fetchmail.attachment.condition",
        "server_id",
        string="Attachment Condition",
        help="Files attached to the emails matching these conditions will be imported "
        "in Odoo as 'Attachment Queue' objects",
    )

    @api.onchange("attachment_condition_ids")
    def onchange_attachment_condition(self):
        for server in self:
            if server.attachment_condition_ids:
                server.object_id = self.env["ir.model"].search(
                    [("model", "=", "attachment.queue")]
                )
                server.attach = True


class FetchmailAttachmentCondition(models.Model):
    _name = "fetchmail.attachment.condition"
    _description = "Fetchmail Attachment Conditions"

    name = fields.Char(string="Condition Name", required=True,)
    email_from = fields.Char(
        string="Email From",
        help="If empty, catches the emails from every senders.\n"
        "Otherwise catches the emails where the sender's email contains the given "
        "characters",
    )
    email_subject = fields.Char(
        string="Email Subject",
        help="If empty, catches the emails with every kind of Subjects.\n"
        "Otherwise catches the emails where the Subject contains the given characters",
    )
    file_extension = fields.Char(
        string="File Extension",
        help="The extension (or part of the name) of the sought files. "
        "If empty, all the email's attachments will be imported.",
    )
    server_id = fields.Many2one("fetchmail.server", string="Server Mail")
    file_type = fields.Selection(
        selection=[],
        help="The 'file type' is transmited to the 'Attachment Queue' objects created "
        "from the selected emails attachments.\nIt will allow Odoo to recognize "
        "what do do with them once created.",
    )
