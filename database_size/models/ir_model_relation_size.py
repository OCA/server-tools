# Copyright 2025 Opener B.V. <https://opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class IrModelRelationSize(models.Model):
    _name = "ir.model.relation.size"
    _description = "Disk space usage of a single many2many table"
    _order = "ir_model_size_id desc, size desc"

    name = fields.Char(required=True)
    ir_model_size_id = fields.Many2one(
        comodel_name="ir.model.size",
        index=True,
        ondelete="cascade",
        required=True,
    )
    size = fields.Integer()
