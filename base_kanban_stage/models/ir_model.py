# Copyright 2019 Eficent Business and IT Consulting Services S.L.
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
            self.pool.setup_models(self.env.cr)
            # update database schema of models
            model_names = self.pool.descendants(self.mapped("model"), "_inherits")
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
    def _instanciate(self, model_data):
        model_class = super()._instanciate(model_data)
        if model_data.get("is_kanban") and model_class._name != "base.kanban.abstract":
            parents = model_class._inherit or []
            parents = [parents] if isinstance(parents, str) else parents
            model_class._inherit = parents + ["base.kanban.abstract"]
        return model_class
