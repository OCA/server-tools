# Copyright 2021 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class RequestRequest(models.Model):
    _name = "request.request"
    _inherit = ["request.request", "base.exception"]
    _order = "main_exception_id asc, name"

    @api.model
    def test_all_draft_request(self):
        request_set = self.search([("state", "=", "draft")])
        request_set.detect_exceptions()
        return True

    @api.model
    def _reverse_field(self):
        return "request_ids"

    def detect_exceptions(self):
        all_exceptions = super().detect_exceptions()
        lines = self.mapped("product_line_ids")
        all_exceptions += lines.detect_exceptions()
        return all_exceptions

    @api.constrains("ignore_exception", "product_line_ids", "state")
    def request_check_exception(self):
        requests = self.filtered(lambda s: s.state == "pending")
        if requests:
            requests._check_exception()

    @api.onchange("product_line_ids")
    def onchange_ignore_exception(self):
        if self.state == "pending":
            self.ignore_exception = False

    def action_confirm(self):
        if self.detect_exceptions() and not self.ignore_exception:
            return self._popup_exceptions()
        return super().action_confirm()

    def action_draft(self):
        res = super().action_draft()
        for order in self:
            order.exception_ids = False
            order.main_exception_id = False
            order.ignore_exception = False
        return res

    @api.model
    def _get_popup_action(self):
        action = self.env.ref("request_flow_exception.action_request_exception_confirm")
        return action

    def _ready_to_submit(self):
        """ Use additional exception rules to check for readiness """
        if not super()._ready_to_submit():
            return False
        rules = self.env["exception.rule"].sudo().search(self._rule_domain())
        for rule in rules:
            records_with_exception = self._detect_exceptions(rule)
            if records_with_exception:
                return False
        return True
