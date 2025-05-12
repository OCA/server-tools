# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class FetchmailServer(models.Model):
    _inherit = "fetchmail.server"

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
