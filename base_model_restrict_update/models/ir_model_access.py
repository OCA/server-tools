# Copyright 2021-2024 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models
from odoo.exceptions import AccessError
from odoo.tools.translate import _


class IrModelAccess(models.Model):
    _inherit = "ir.model.access"

    @api.model
    def _readonly_exclude_models(self):
        """Models update/create by system, and should be excluded from checking"""
        self.env.cr.execute(
            """
            SELECT m.model
            FROM ir_model_access ma
            JOIN ir_model m ON ma.model_id = m.id
            WHERE ma.group_id IS NULL
              AND (
                ma.perm_write = TRUE
                OR ma.perm_create = TRUE
                OR ma.perm_unlink = TRUE
              )
            """,
        )
        return self.env.cr.fetchall()

    @api.model
    def _test_readonly(self, model):
        if not self.env.user.is_readonly_user:
            return False
        if (model,) in self._readonly_exclude_models():
            return False
        models_to_exclude = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("base_model_restrict_update.excluded_models_from_readonly", "")
        )
        if model in models_to_exclude:
            return False
        return True

    @api.model
    def _test_restrict_update(self, model):
        # Get the IDs of unresticted users for the model if it's restricted
        self.env.cr.execute(
            """
            SELECT gurel.uid
            FROM ir_model m
            LEFT JOIN ir_model_res_groups_update_allowed_rel mgrel
              ON m.id = mgrel.ir_model_id
            LEFT JOIN res_groups_users_rel gurel
              ON mgrel.res_groups_id = gurel.gid
            WHERE m.model = %s
              AND m.restrict_update = true
            """,
            (model,),
        )
        query_res = self.env.cr.fetchall()
        return bool(query_res) and (self.env.uid,) not in query_res

    @api.model
    def check(self, model, mode="read", raise_exception=True):
        if self.env.su:
            return True
        res = super().check(model, mode=mode, raise_exception=raise_exception)
        if mode == "read":
            return res
        if self._test_readonly(model) or self._test_restrict_update(model):
            if not raise_exception:
                return False
            raise AccessError(
                _("You are only allowed to read this record. (%(model)s - %(mode)s)")
                % {"model": model, "mode": mode}
            )
        return res
