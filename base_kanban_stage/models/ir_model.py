# Copyright 2025 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError


class IrModel(models.Model):
    _inherit = "ir.model"

    is_kanban = fields.Boolean(
        string="Kanban",
        default=False,
        help="Whether this model support kanban stages.",
    )

    def write(self, vals):
        if self and "is_kanban" in vals:
            if any(rec.state != "manual" for rec in self):
                raise UserError(self.env._("Only custom models can be modified."))
            if any(rec.is_kanban > vals["is_kanban"] for rec in self):
                raise UserError(
                    self.env._('Field "Kanban" cannot be changed to "False".')
                )
            res = super().write(vals)
            self.env.flush_all()
            # setup models; this reloads custom models in registry
            model_names = self.mapped("model")
            self.pool._setup_models__(self.env.cr, model_names)
            # update database schema of models
            model_names = self.pool.descendants(model_names, "_inherits")
            self.pool.init_models(
                self.env.cr,
                model_names,
                dict(self.env.context, update_custom_fields=True),
            )
        else:
            res = super().write(vals)
        return res

    def _reflect_model_params(self, model):
        vals = super()._reflect_model_params(model)
        vals["is_kanban"] = isinstance(model, self.pool["base.kanban.abstract"])
        return vals

    @api.model
    def _instanciate_attrs(self, model_data):
        attrs = super()._instanciate_attrs(model_data)
        if model_data.get("is_kanban") and attrs["_name"] != "base.kanban.abstract":
            parents = attrs.get("_inherit") or []
            parents = [parents] if isinstance(parents, str) else parents
            attrs["_inherit"] = parents + ["base.kanban.abstract"]
        return attrs
