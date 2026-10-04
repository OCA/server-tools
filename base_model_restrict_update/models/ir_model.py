# Copyright 2021-2024 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class IrModel(models.Model):
    _inherit = "ir.model"

    restrict_update = fields.Boolean(
        "Update Restrict Model",
        help="When selected, the model is restricted to read-only unless the "
        "user belongs to an Update-Allowed Group.",
    )
    update_allowed_group_ids = fields.Many2many(
        "res.groups",
        "ir_model_res_groups_update_allowed_rel",
        string="Update-Allowed Groups",
    )
