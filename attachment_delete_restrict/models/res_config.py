# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .ir_model import RESTRICT_DELETE_ATTACH


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    global_restrict_delete_attachment = fields.Selection(
        selection=RESTRICT_DELETE_ATTACH,
        config_parameter="attachment_delete_restrict.global_restrict_delete_attachment",
        readonly=False,
        required=True,
        default="none",
        string="Restrict Delete Attachments",
        help="Define a default value for Attachments Deletion",
    )

    global_delete_attachment_group_ids = fields.Many2many(
        "res.groups",
        string="Attachment Deletion Groups",
        relation="global_delete_attachment_group_rel",
        help="The users in the groups selected here can delete all the attachments.",
        readonly=False,
        compute="_compute_global_delete_attachment_group_ids",
        inverse="_inverse_global_delete_attachment_group_ids",
    )
    global_delete_attachment_group_ids_str = fields.Char(
        string="",
        config_parameter="attachment_delete_restrict.global_delete_attachment_group_ids",
    )

    global_delete_attachment_user_ids = fields.Many2many(
        "res.users",
        string="Attachment Deletion Users",
        relation="global_delete_attachment_user_rel",
        help="The users selected here can delete all the attachments",
        readonly=False,
        compute="_compute_global_delete_attachment_user_ids",
        inverse="_inverse_global_delete_attachment_user_ids",
    )

    global_delete_attachment_user_ids_str = fields.Char(
        string="",
        config_parameter="attachment_delete_restrict.global_delete_attachment_user_ids",
    )

    @api.depends("global_delete_attachment_group_ids_str")
    def _compute_global_delete_attachment_group_ids(self):
        for setting in self:
            if setting.global_delete_attachment_group_ids_str:
                ids = setting.global_delete_attachment_group_ids_str.split(",")
                setting.global_delete_attachment_group_ids = self.env[
                    "res.groups"
                ].search([("id", "in", ids)])
            else:
                setting.global_delete_attachment_group_ids = None

    def _inverse_global_delete_attachment_group_ids(self):
        for setting in self:
            if setting.global_delete_attachment_group_ids:
                setting.global_delete_attachment_group_ids_str = ",".join(
                    str(setting.global_delete_attachment_group_ids.mapped("id"))
                )
            else:
                setting.global_delete_attachment_group_ids_str = ""

    @api.depends("global_delete_attachment_user_ids_str")
    def _compute_global_delete_attachment_user_ids(self):
        for setting in self:
            if setting.global_delete_attachment_user_ids_str:
                ids = setting.global_delete_attachment_user_ids_str.split(",")
                setting.global_delete_attachment_user_ids = self.env["res.user"].search(
                    [("id", "in", ids)]
                )
            else:
                setting.global_delete_attachment_user_ids = None

    def _inverse_global_delete_attachment_user_ids(self):
        for setting in self:
            if setting.global_delete_attachment_user_ids:
                setting.global_delete_attachment_user_ids_str = ",".join(
                    str(setting.global_delete_attachment_user_ids.mapped("id"))
                )
            else:
                setting.global_delete_attachment_user_ids_str = ""
