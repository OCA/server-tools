# Copyright 2026 Heligrafics Fotogrametria S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SearchDateWindowTest(models.Model):
    _name = "search.date.window.test"
    _inherit = "search.date.window.mixin"
    _description = "Search Date Window Test"

    _date_window_past_field = "date_start"
    _date_window_past_days = 7
    _date_window_future_field = "date_end"
    _date_window_future_days = 1

    name = fields.Char()
    date_start = fields.Datetime()
    date_end = fields.Datetime()
    day = fields.Date()
    parent_id = fields.Many2one("search.date.window.test")
    child_ids = fields.One2many("search.date.window.test", "parent_id")
    # no inverse field: invalidating ref_name needs a search
    ref_id = fields.Many2one("search.date.window.test")
    ref_name = fields.Char(compute="_compute_ref_name", store=True)

    @api.depends("ref_id.name")
    def _compute_ref_name(self):
        for record in self:
            record.ref_name = record.ref_id.name
