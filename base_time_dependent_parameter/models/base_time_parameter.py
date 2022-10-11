# Author Copyright (C) 2022 Nimarosa (Nicolas Rodriguez) (<nicolasrsande@gmail.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ast import literal_eval

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class BaseTimeParameter(models.Model):
    _name = "base.time_parameter"
    _description = "Time Parameter"

    name = fields.Char(required=True, string="Parameter Name")
    code = fields.Char(required=True, string="Code")
    description = fields.Text("Description")
    country_id = fields.Many2one(
        "res.country",
        string="Country",
        default=lambda self: self.env.company.country_id,
    )
    parameter_version_ids = fields.One2many(
        "base.time_parameter.value", "time_parameter_id", string=("Versions")
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        default=lambda self: self.env.company,
    )

    @api.model
    def _get_parameter_from_code(self, code, date=None):
        if not date:
            date = fields.Date.today()
        parameter = self.env["base.time_parameter.value"].search(
            [
                ("code", "=", code),
                ("date_from", "<=", date),
                ("company_id", "=", self.env.company.id),
            ],
            limit=1,
        )
        if parameter:
            return literal_eval('"{}"'.format(parameter.parameter_value))
        else:
            raise UserError(
                _("No rule parameter with code '%s' was found for date %s")
                % (code, date)
            )

    _sql_constraints = [
        (
            "_unique",
            "unique (code, company_id)",
            "Two time parameters cannot have the same code.",
        ),
    ]
