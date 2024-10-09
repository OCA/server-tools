# Copyright 2021 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

RESTRICT_DELETE_ATTACH = [
    ("default", "Use global configuration"),
    ("owner", "Owner: Only creator and admin can delete them"),
    ("custom", "Custom: For each model, selected groups and users can delete them"),
    (
        "owner_custom",
        "Owner + Custom: Creator and admin can delete them + for "
        "each model, selected groups and users can delete them",
    ),
    ("none", "No restriction: All users / groups can delete them"),
]


class IrModel(models.Model):
    _inherit = "ir.model"

    restrict_delete_attachment = fields.Selection(
        selection=RESTRICT_DELETE_ATTACH,
        string="Restrict Attachment Deletion",
        help="When selected, the deletion of the attachments related to this model is "
        "restricted to certain users.",
        default="default",
    )

    delete_attachment_group_ids = fields.Many2many(
        "res.groups",
        string="Attachment Deletion Groups",
        relation="delete_attachment_group_rel",
        help="The users in the groups selected here can delete the attachments related "
        "to this model.",
    )

    delete_attachment_user_ids = fields.Many2many(
        "res.users",
        string="Attachment Deletion Users",
        relation="delete_attachment_user_rel",
        help="The users selected here can delete the attachments related to this "
        "model.",
    )

    def _onchange_restrict_delete_attachment(self):
        if self.restrict_delete_attachment not in ["custom", "owner_custom"]:
            self.delete_attachment_group_ids = False
            self.delete_attachment_user_ids = False
