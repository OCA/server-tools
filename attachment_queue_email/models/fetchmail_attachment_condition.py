# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class FetchmailAttachmentCondition(models.Model):
    _name = "fetchmail.attachment.condition"
    _description = "Fetchmail Attachment Conditions"
    _check_company_auto = True

    name = fields.Char(
        string="Condition Name",
        required=True,
    )
    email_from = fields.Char(
        help="If empty, catches the emails from every senders.\n"
        "Otherwise catches the emails where the sender's email contains the given "
        "characters",
    )
    email_to = fields.Char(
        help="If empty, catches the email no matter the recipient.\n"
        "Otherwise catches the emails where the recipients emails contains the given "
        "characters.",
    )
    email_subject = fields.Char(
        help="If empty, catches the emails with every kind of Subjects.\n"
        "Otherwise catches the emails where the Subject contains the given characters",
    )
    file_extension = fields.Char(
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
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
