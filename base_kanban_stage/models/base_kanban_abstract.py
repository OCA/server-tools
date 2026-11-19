from odoo import api, fields, models


class BaseKanbanAbstract(models.AbstractModel):
    _name = "base.kanban.abstract"
    _description = "Kanban Abstract"

    stage_id = fields.Many2one(
        "base.kanban.stage",
        "Kanban Stage",
        default=lambda self: self._default_stage_id(),
        group_expand="_read_group_stage_ids",
    )
    kanban_state = fields.Selection(
        [
            ("normal", "Normal"),
            ("done", "Done"),
            ("blocked", "Blocked"),
        ],
        default="normal",
    )
    kanban_priority = fields.Selection(
        [
            ("0", "Low"),
            ("1", "Medium"),
            ("2", "High"),
        ],
        string="Priority",
        default="1",
    )
    kanban_color = fields.Integer("Color Index")
    kanban_sequence = fields.Integer()
    user_id = fields.Many2one("res.users", "Assigned to")

    @api.model
    def _default_stage_id(self):
        return self.env["base.kanban.stage"].search(
            [("res_model_id.model", "=", self._name)],
            order="sequence",
            limit=1,
        )

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env["base.kanban.stage"].search(
            [("res_model_id.model", "=", self._name)],
            order=order,
        )
