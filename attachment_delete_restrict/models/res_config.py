# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ast import literal_eval

from odoo import api, fields, models

from .ir_model import RESTRICT_DELETE_ATTACH


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    global_restrict_delete_attachment = fields.Selection(
        selection=RESTRICT_DELETE_ATTACH[1:],
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
        help="The users in the groups selected here can delete all the attachments.",
        readonly=False,
        compute_sudo=True,
        compute="_compute_global_delete_attachment_group_ids",
        inverse="_inverse_global_delete_attachment_group_ids",
    )
    global_delete_attachment_user_ids = fields.Many2many(
        "res.users",
        string="Attachment Deletion Users",
        help="The users selected here can delete all the attachments",
        readonly=False,
        compute_sudo=True,
        compute="_compute_global_delete_attachment_user_ids",
        inverse="_inverse_global_delete_attachment_user_ids",
    )

    def _get_global_delete_attachment_groups(self):
        str_group_ids = self.env["ir.config_parameter"].get_param(
            "attachment_delete_restrict.global_delete_attachment_group_ids"
        )
        groups_ids = literal_eval(str_group_ids or "[]")
        return self.env["res.groups"].search([("id", "in", groups_ids)])

    @api.depends("global_restrict_delete_attachment")
    def _compute_global_delete_attachment_group_ids(self):
        groups = self._get_global_delete_attachment_groups()
        for setting in self:
            if "custom" in setting.global_restrict_delete_attachment:
                setting.global_delete_attachment_group_ids = groups
            else:
                setting.global_delete_attachment_group_ids = None

    def _inverse_global_delete_attachment_group_ids(self):
        for setting in self:
            self.env["ir.config_parameter"].set_param(
                "attachment_delete_restrict.global_delete_attachment_group_ids",
                str(setting.global_delete_attachment_group_ids.ids),
            )

    def _get_global_delete_attachment_users(self):
        str_user_ids = self.env["ir.config_parameter"].get_param(
            "attachment_delete_restrict.global_delete_attachment_user_ids"
        )
        user_ids = literal_eval(str_user_ids or "[]")
        return self.env["res.users"].search([("id", "in", user_ids)])

    @api.depends("global_restrict_delete_attachment")
    def _compute_global_delete_attachment_user_ids(self):
        users = self._get_global_delete_attachment_users()
        for setting in self:
            if "custom" in setting.global_restrict_delete_attachment:
                setting.global_delete_attachment_user_ids = users
            else:
                setting.global_delete_attachment_user_ids = None

    def _inverse_global_delete_attachment_user_ids(self):
        for setting in self:
            self.env["ir.config_parameter"].set_param(
                "attachment_delete_restrict.global_delete_attachment_user_ids",
                str(setting.global_delete_attachment_user_ids.ids),
            )
