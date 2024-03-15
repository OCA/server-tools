# Copyright 2021 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RequestCategory(models.Model):
    _inherit = "request.category"

    custom_info_template_id = fields.Many2one(
        comodel_name="custom.info.template",
        domain=[("model", "=", "request.request")],
    )
