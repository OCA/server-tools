# Copyright 2021 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, tools
from odoo.exceptions import AccessError
from odoo.tools.translate import _


class IrModelAccess(models.Model):
    _inherit = "ir.model.access"

    @api.model
    @tools.ormcache_context(
        "self.env.uid",
        "model",
        "mode",
        "raise_exception",
        keys=("lang",)
    )
    def check(self, model, mode="read", raise_exception=True):
        res = super(IrModelAccess, self).check(model, mode, raise_exception)
        if self._uid == 1:
            return True
        if mode != "read" and raise_exception:
            if self._test_readonly(model) or self._test_restrict_update(model):
                raise AccessError(
                    _("You are only allowed to read this record. (%s - %s)")
                    % (model, mode)
                )
        return res

    @api.model
    def _test_readonly(self, model):
        exclude_models = self._readonly_exclude_models()
        if model not in exclude_models and self.env.user.is_readonly_user:
            return True
        return False

    @api.model
    def _test_restrict_update(self, model):
        self.env.cr.execute(
            "SELECT restrict_update FROM ir_model WHERE model = %s", (model,)
        )
        query_res = self.env.cr.dictfetchone()
        if query_res["restrict_update"] and not self.env.user.unrestrict_model_update:
            return True
        return False

    @api.model
    def _readonly_exclude_models(self):
        """ Models updtate/create by system, and should be excluded from checking """
        return self.sudo().search([
            ("group_id", "=", False),
            "|", ("perm_write", "=", True),
            "|", ("perm_create", "=", True), ("perm_unlink", "=", True)
        ]).mapped("model_id.model")
