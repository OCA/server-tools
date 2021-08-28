# Copyright 2021 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    @api.multi
    def unlink(self):
        for rec in self:
            if not rec.res_model:
                continue
            model = self.env["ir.model"].search(
                [
                    ("model", "=", rec.res_model),
                    ("restrict_delete_attachment", "=", True),
                ]
            )
            if not model:
                continue
            groups = model.delete_attachment_group_ids
            if groups and self.env.user in groups.mapped("users"):
                continue
            users = model.delete_attachment_user_ids
            if users and self.env.user in users:
                continue
            user_names = "\n".join(
                list(set(groups.mapped("users").mapped("name") + users.mapped("name")))
            )
            raise ValidationError(
                _(
                    "You are not allowed to delete this attachment.\n\nUsers with "
                    "the delete permission:\n%s"
                )
                % (user_names or "None")
            )
        return super().unlink()
