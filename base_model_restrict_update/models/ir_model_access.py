# Copyright 2021 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, tools
from odoo.exceptions import AccessError
from odoo.tools.translate import _


class IrModelAccess(models.Model):
    _inherit = "ir.model.access"

    @api.model
    @tools.ormcache_context(
        "self._uid", "model", "mode", "raise_exception", keys=("lang",)
    )
    def check(self, model, mode="read", raise_exception=True):
        res = super(IrModelAccess, self).check(model, mode, raise_exception)
        if self._uid == 1:
            return True
        self._cr.execute(
            "SELECT restrict_update FROM ir_model WHERE model = %s", (model,)
        )
        query_res = self._cr.dictfetchall()[0]
        if (
            query_res["restrict_update"]
            and mode != "read"
            and not self.env.user.unrestrict_model_update
        ):
            if raise_exception:
                raise AccessError(
                    _("You are only allowed to read this record. (%s - %s)")
                    % (model, mode)
                )
            return False
        return res
