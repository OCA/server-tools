# Author Copyright (C) 2022 Nimarosa (Nicolas Rodriguez) (<nicolasrsande@gmail.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
from datetime import datetime

from odoo import api, fields, models


def _validate_boolean(value):
    if value in ("True", "true", "TRUE", "1"):
        return "True"
    elif value in ("False", "false", "FALSE", "0"):
        return "False"


def _validate_date(value, date_format):
    date_formats = [date_format, "%Y-%m-%d"]
    for date_format in date_formats:
        try:
            return datetime.strptime(value, date_format).strftime("%Y-%m-%d")
        except ValueError:
            pass


def _validate_float(value):
    try:
        return str(float(value))
    except ValueError:
        pass


def _validate_integer(value):
    try:
        return str(int(round(float(value), 0)))
    except ValueError:
        pass


def _validate_json(value):
    try:
        json.loads(value)
        return value
    except ValueError:
        pass


class TimeParameterVersion(models.Model):
    _name = "base.time.parameter.version"
    _description = "Time Parameter Version"
    _order = "date_from desc"

    parameter_id = fields.Many2one(
        "base.time.parameter",
        required=True,
        ondelete="cascade",
        string="Time Parameter",
    )
    country_id = fields.Many2one(related="parameter_id.country_id")
    company_id = fields.Many2one(related="parameter_id.company_id", store=True)
    code = fields.Char(related="parameter_id.code", store=True, readonly=True)
    date_from = fields.Date(string="Date From", required=True)
    type = fields.Selection(related="parameter_id.type")
    value = fields.Char(string="Value")
    value_reference = fields.Reference(string="Reference Value", selection=[])

    _sql_constraints = [
        (
            "_unique",
            "unique (parameter_id, date_from)",
            "A parameter cannot have two versions starting the same day.",
        ),
    ]

    @api.onchange("value")
    def _onchange_value(self):
        if self.value:
            if self.type == "date":
                date_format = (
                    self.env["res.lang"]
                    .search([("code", "=", self.env.user.lang)])
                    .ensure_one()
                    .date_format
                )
                self.value = _validate_date(self.value, date_format)
            elif self.type == "string":
                pass
            else:
                method = "_validate_{}".format(self.type)
                self.value = globals()[method](self.value)
