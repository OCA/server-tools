# Copyright 2021 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RequestExceptionConfirm(models.TransientModel):
    _name = "request.exception.confirm"
    _description = "Request exception wizard"
    _inherit = ["exception.rule.confirm"]

    related_model_id = fields.Many2one("request.request", "request")

    def action_confirm(self):
        self.ensure_one()
        if self.ignore:
            self.related_model_id.action_draft()
            self.related_model_id.ignore_exception = True
            self.related_model_id.action_confirm()
        return super().action_confirm()
