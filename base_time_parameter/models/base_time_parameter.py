# Author Copyright (C) 2022 Nimarosa (Nicolas Rodriguez) (<nicolasrsande@gmail.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class TimeParameter(models.Model):
    _name = "base.time.parameter"
    _description = "Time Parameter"

    name = fields.Char(string="Parameter Name")
    code = fields.Char(string="Code")
    description = fields.Text("Description")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    country_id = fields.Many2one(
        "res.country",
        string="Country",
        default=lambda self: self.env.company.country_id,
    )
    model_id = fields.Many2one(
        "ir.model",
        string="Model",
        help="Filter by model (e.g. hr.payslip)",
    )
    type = fields.Selection(
        [
            ("boolean", "Boolean (True/False)"),
            ("date", "Date"),
            ("float", "Floating point number"),
            ("integer", "Integer number"),
            ("json", "JSON"),
            ("record", "Record"),
            ("string", "Text"),
        ],
        required=True,
        default="float",
        index=True,
    )
    record_model = fields.Selection([], string="Record Model")
    version_ids = fields.One2many(
        "base.time.parameter.version", "parameter_id", string=("Versions")
    )

    @api.model
    def _get_from_model_code_date(
        self, model_name, code, date=None, raise_if_not_found=True, get="value"
    ):
        # Filter on company, model, code/name
        model = self.env["ir.model"].search([("model", "=", model_name)])
        domain = [
            "&",
            ("company_id", "in", (self.env.company.id, False)),
            "&",
            ("model_id", "in", (model.id, False)),
            "|",
            ("code", "=", code),
            "&",
            ("code", "=", False),
            ("name", "=", code),
        ]
        parameter = self.env["base.time.parameter"].search(domain)
        if parameter:
            return parameter._get(date, get=get)
        # No value
        if not raise_if_not_found:
            return
        # Raise error
        model_name = model.name
        raise UserError(
            _("No parameter for model '%(model_name)s', code '%(code)s', date %(date)s")
            % (model_name, code, date)
        )

    def _get(self, date=None, get="value"):
        self.ensure_one()
        if not date:
            date = fields.Date.today()
        versions = self.version_ids.filtered(lambda v: v.date_from <= date).sorted(
            key=lambda v: v.date_from, reverse=True
        )
        if not versions:
            return False
        version = versions[0]
        if get == "value":
            return self._get_value(version)
        elif get == "date":
            return version.date_from

    def _get_value(self, version):
        if self.type == "boolean":
            return version.value == "True" and True or False
        elif self.type == "date":
            return datetime.strptime(version.value, "%Y-%m-%d").date()
        elif self.type == "float":
            return float(version.value)
        elif self.type == "integer":
            return int(version.value)
        elif self.type == "json":
            return json.loads(version.value)
        elif self.type == "record" and not self.record_model:
            return version.value_reference
        elif self.type == "string":
            return version.value

    _sql_constraints = [
        (
            "_unique",
            "unique (code, company_id)",
            "Two time parameters cannot have the same code.",
        ),
    ]
