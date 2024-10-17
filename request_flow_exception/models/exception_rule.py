# Copyright 2021 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ExceptionRule(models.Model):
    _inherit = "exception.rule"

    request_ids = fields.Many2many(comodel_name="request.request", string="Requests")
    model = fields.Selection(
        selection_add=[
            ("request.request", "Requests"),
            ("request.product.line", "Request product line"),
        ],
        ondelete={
            "request.request": "cascade",
            "request.product.line": "cascade",
        },
    )
