from odoo import api, fields, models


class BaseKanbanStage(models.Model):
    _name = "base.kanban.stage"
    _description = "Kanban Stage"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean(help="Used to hide the stage")
    res_model_id = fields.Many2one(
        "ir.model",
        string="Related Model",
        required=True,
        ondelete="cascade",
        default=lambda self: self._default_res_model_id(),
    )
    legend_blocked = fields.Text(string="Red Rules")
    legend_done = fields.Text(string="Green Rules")
    legend_normal = fields.Text(string="Yellow Rules")
    kanban_legend = fields.Text()
    active = fields.Boolean(default=True)

    @api.model
    def _default_res_model_id(self):
        action_id = self.env.context.get("default_res_model_id")
        if action_id:
            return action_id
        action_id = self.env.context.get("params", {}).get("action")
        if action_id:
            action = self.env["ir.actions.act_window"].browse(action_id).exists()
            if action:
                model = self.env["ir.model"].search(
                    [("model", "=", action.res_model)],
                    limit=1,
                )
                if model and model.model != self._name:
                    return model.id
        return False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "sequence" not in vals:
                last = self.search(
                    [("res_model_id", "=", vals.get("res_model_id"))],
                    order="sequence desc",
                    limit=1,
                )
                vals["sequence"] = (last.sequence + 1) if last else 1
        return super().create(vals_list)
