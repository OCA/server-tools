from odoo import fields, models


class IrModel(models.Model):
    _inherit = "ir.model"

    is_kanban = fields.Boolean(default=False)
