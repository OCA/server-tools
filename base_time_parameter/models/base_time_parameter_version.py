# Author Copyright (C) 2022 Nimarosa (Nicolas Rodriguez) (<nicolasrsande@gmail.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import api, fields, models


def _validate(value, data_type, date_format=None):
    """
    Validate the value according to the data type.

    :param value: string
    :param data_type: string ("boolean"/"date"/"float"/"integer"/"string")
    :param date_format: string

    :return: Modified value, or None if the value doesn't match the data type.
    """
    # All values are strings
    new_value = ""

    if data_type == "boolean":
        if value in ("True", "true", "TRUE", "1"):
            new_value = "True"
        elif value in ("False", "false", "FALSE", "0"):
            new_value = "False"

    elif data_type == "date":
        date_formats = ["%Y-%m-%d", date_format]
        # _logger.debug("formats: " + str(formats) + ", value = " + str(value))
        for date_format in date_formats:
            try:
                new_value = datetime.strptime(value, date_format).strftime("%Y-%m-%d")
                break
            except ValueError:
                pass

    elif data_type == "float":
        try:
            new_value = str(float(value))
        except ValueError:
            pass

    elif data_type == "integer":
        try:
            new_value = str(int(round(float(value), 0)))
        except ValueError:
            pass

    elif data_type == "string":
        new_value = value

    return new_value


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
    value_reference = fields.Reference(
        string="Reference Value",
        selection="_value_reference_selection",
    )

    @api.model
    def _value_reference_selection(self):
        model_names = self.env.context.get("selection_models", [])
        models = self.env["ir.model"].search([("model", "in", model_names)])
        return [(m.model, m.name) for m in models]

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
            date_format = None
            if self.type == "date":
                date_format = (
                    self.env["res.lang"]
                    .search([("code", "=", self.env.user.lang)])
                    .ensure_one()
                    .date_format
                )
            self.value = _validate(self.value, self.type, date_format)
