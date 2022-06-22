# Author Copyright (C) 2022 Nimarosa (Nicolas Rodriguez) (<nicolasrsande@gmail.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrSalaryRuleParameterValue(models.Model):
    _name = "base.time_parameter.value"
    _description = "Time Parameter Value"
    _order = "date_from desc"

    time_parameter_id = fields.Many2one(
        "base.time_parameter",
        required=True,
        ondelete="cascade",
        string="Time Parameter",
    )
    country_id = fields.Many2one(related="time_parameter_id.country_id")
    company_id = fields.Many2one(related="time_parameter_id.company_id")
    code = fields.Char(related="time_parameter_id.code", store=True, readonly=True)
    date_from = fields.Date(string="Date From", required=True)
    parameter_value = fields.Text(help="Python Code")

    _sql_constraints = [
        (
            "_unique",
            "unique (time_parameter_id, date_from)",
            "Two rules parameters with the same code cannot start the same day",
        ),
    ]
