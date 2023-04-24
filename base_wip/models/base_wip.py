# Copyright 2019 KMEE INFORMÁTICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

from odoo import api, fields, models

intervals = (
    ("w", 604800),  # 60 * 60 * 24 * 7
    ("days", 86400),  # 60 * 60 * 24
    ("hours", 3600),  # 60 * 60
    ("min", 60),
    ("sec", 1),
)


def display_time(seconds, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip("s")
            result.append("{} {}".format(int(value), name))
    return ", ".join(result[:granularity])


class BaseWip(models.Model):
    _name = "base.wip"
    _description = "Base Wip"

    @api.model
    def _get_states(self):
        return [
            ("draft", "New"),
            ("open", "In Progress"),
            ("pending", "Pending"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
            ("exception", "Exception"),
        ]

    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Model",
        index=True,
    )

    res_id = fields.Integer(
        string="Resource ID",
        index=True,
    )

    state = fields.Selection(
        selection=[
            ("running", "Running"),
            ("closed", "Closed"),
        ],
        default="running",
        required=True,
        index=True,
    )

    date_hour_start = fields.Datetime(
        string="Start",
        default=fields.Datetime.now,
        required=True,
        index=True,
    )

    date_start = fields.Date(
        default=fields.Date.context_today,
        required=False,
        index=True,
    )

    date_hour_stop = fields.Datetime(
        string="Stop",
        required=False,
        index=True,
    )

    date_stop = fields.Date(
        required=False,
        index=True,
    )

    lead_time_seconds = fields.Float(
        string="Lead Time Float",
        compute="_compute_lead_time",
    )

    lead_time = fields.Char(
        compute="_compute_lead_time",
    )

    wip_state = fields.Selection(
        selection=_get_states,
        string="State",
        index=True,
    )

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        required=False,
        default=lambda self: self.env.uid,
        index=True,
    )

    @api.depends("date_hour_stop", "date_hour_start")
    def _compute_lead_time(self):
        for blocktime in self:

            d1 = fields.Datetime.to_datetime(blocktime.date_hour_start)
            if blocktime.date_hour_stop:
                d2 = fields.Datetime.to_datetime(blocktime.date_hour_stop)
            else:
                d2 = datetime.datetime.now()
            diff = d2 - d1

            blocktime.lead_time = display_time(diff.total_seconds(), 5)
            blocktime.lead_time_seconds = diff.total_seconds()

    def stop(self):
        for record in self.filtered(lambda o: o.state == "running"):
            record.write(
                {
                    "state": "closed",
                    "date_hour_stop": fields.Datetime.now(),
                    "date_stop": fields.Date.context_today(self),
                }
            )

    def start(self, model_id, res_id, wip_state="draft"):
        if wip_state != "cancelled":
            self.env["base.wip"].create(
                {
                    "model_id": self.env["ir.model"]
                    .search([("model", "=", model_id)])
                    .id,
                    "res_id": res_id,
                    "wip_state": wip_state,
                }
            )
