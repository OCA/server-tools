# Copyright 2021 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ast import literal_eval

from odoo import _, models
from odoo.exceptions import ValidationError


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def _check_delete_attachment(self, model, restrict, mode):
        if restrict == "restrict":
            if self._check_restrict_delete_attachment():
                return
            else:
                self._raise_restrict_validation_error()
        elif restrict == "custom":
            self._check_custom_delete_attachment(model, mode)
        elif restrict == "restrict_custom":
            if self._check_restrict_delete_attachment():
                return
            self._check_custom_delete_attachment(model, mode)

    def _check_restrict_delete_attachment(self):
        if self.create_uid == self.env.user or self.user_has_groups(
            "base.group_system"
        ):
            return True
        else:
            return False

    def _check_custom_delete_attachment(self, model, mode):
        if not model and mode != "global":
            return
        groups = model.delete_attachment_group_ids
        users = model.delete_attachment_user_ids
        param = self.env["ir.config_parameter"].sudo()
        groups_ids = param.get_param(
            "attachment_delete_restrict.global_delete_attachment_group_ids"
        )
        users_ids = param.get_param(
            "attachment_delete_restrict.global_delete_attachment_user_ids"
        )
        if mode == "global":
            if groups_ids:
                groups = self.env["res.groups"].search(
                    [("id", "in", literal_eval(groups_ids))]
                )
            if users_ids:
                users = self.env["res.users"].search(
                    [("id", "in", literal_eval(users_ids))]
                )
        if groups and self.env.user in groups.mapped("users"):
            return
        if users and self.env.user in users:
            return
        list_group = "\n".join(list(set(groups.mapped("users").mapped("name"))))
        list_user = "\n".join(list(set(users.mapped("name"))))
        user_names = list_group + list_user
        raise ValidationError(
            _(
                "You are not allowed to delete this attachment.\n\nUsers with "
                "the delete permission:\n%s"
            )
            % (user_names or "None")
        )

    def _raise_restrict_validation_error(self):
        raise ValidationError(
            _(
                "You are not allowed to delete this attachment.\n"
                "Only the owner and administrators can delete it."
            )
        )

    def unlink(self):
        for rec in self:
            if not rec.res_model:
                continue
            model = self.env["ir.model"].search([("model", "=", rec.res_model)])
            model_restrict = model.restrict_delete_attachment
            global_restrict = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(
                    "attachment_delete_restrict.global_restrict_delete_attachment"
                )
            )
            if model_restrict == "default":
                rec._check_delete_attachment(model, global_restrict, "global")
            elif model_restrict not in ["default", "none"]:
                rec._check_delete_attachment(model, model_restrict, "model")
        return super().unlink()
