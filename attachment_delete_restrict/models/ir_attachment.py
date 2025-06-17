# Copyright 2021 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _, models
from odoo.exceptions import ValidationError


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def _check_delete_attachment(self, model=None):
        if model:
            restrict = model.restrict_delete_attachment
        else:
            restrict = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(
                    "attachment_delete_restrict.global_restrict_delete_attachment"
                )
            )
        if restrict == "owner":
            self._check_owner_delete_attachment()
        elif restrict == "custom":
            self._check_custom_delete_attachment(model)
        elif restrict == "owner_custom":
            self._check_custom_delete_attachment(model, allow_owner_and_admin=True)

    def _raise_delete_attachment_error(self, allowed_users):
        raise ValidationError(
            _(
                "You are not allowed to delete this attachment.\n\nUsers with "
                "the delete permission:\n%s"
            )
            % ("\n".join(allowed_users.mapped("name")) or "None")
        )

    def _check_owner_delete_attachment(self):
        if not (
            self.create_uid == self.env.user
            or self.env.user.has_group("base.group_system")
        ):
            return self._raise_delete_attachment_error(
                self.create_uid | self.env.ref("base.group_system").users
            )

    def _check_custom_delete_attachment(self, model=None, allow_owner_and_admin=False):
        if model:
            groups = model.delete_attachment_group_ids
            users = model.delete_attachment_user_ids
        else:
            groups = self.env[
                "res.config.settings"
            ]._get_global_delete_attachment_groups()
            users = self.env[
                "res.config.settings"
            ]._get_global_delete_attachment_users()
        if allow_owner_and_admin:
            users += self.create_uid
            groups += self.env.ref("base.group_system")
        allowed_users = groups.users | users
        if self.env.user not in allowed_users:
            return self._raise_delete_attachment_error(allowed_users)

    def unlink(self):
        if self.env.su:
            return super().unlink()
        res_models = list(set(self.filtered("res_model").mapped("res_model")))
        if res_models:
            models = self.env["ir.model"].sudo().search([("model", "in", res_models)])
            name2models = {m.model: m for m in models}
            for rec in self:
                if rec.res_model:
                    model = name2models[rec.res_model]
                    if (
                        model.restrict_delete_attachment == "default"
                        or not model.restrict_delete_attachment
                    ):
                        rec.sudo()._check_delete_attachment()
                    else:
                        rec.sudo()._check_delete_attachment(model)
        return super().unlink()
