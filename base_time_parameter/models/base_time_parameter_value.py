# Author Copyright (C) 2022 Nimarosa (Nicolas Rodriguez) (<nicolasrsande@gmail.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TimeParameterValue(models.Model):
    _name = "base.time.parameter.value"
    _description = "Time Parameter Value"
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
    value_text = fields.Text(string="Text")
    value_reference = fields.Reference(
        string="Reference",
        selection="_value_reference_selection",
    )

    @api.model
    def _value_reference_selection(self):
        model_names = ["account.account"]
        models = self.env["ir.model"].search([("model", "in", model_names)])
        return [(m.model, m.name) for m in models]

    _sql_constraints = [
        (
            "_unique",
            "unique (parameter_id, date_from, company_id)",
            "Two values of the same parameter cannot start the same day",
        ),
    ]
