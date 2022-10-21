# Author Copyright (C) 2022 Nimarosa (Nicolas Rodriguez) (<nicolasrsande@gmail.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ast import literal_eval

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
            ("text", "Text"),
            ("reference", "Reference"),
        ],
        required=True,
        default="text",
        index=True,
    )
    value_ids = fields.One2many(
        "base.time.parameter.value", "parameter_id", string=("Versions")
    )

    @api.model
    def _get_value_from_model_code_date(self, model_name, code, date=None):
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
            value = parameter._get_value(date)
            if value:
                return value

        # No value, raise error
        model_name = model.name
        # payroll FIXME: Payslip (Compute Sheet) returns another error ...
        raise UserError(
            _("No parameter for model '%(model_name)s', code '%(code)s', date %(date)s")
            % (model_name, code, date)
        )

    def _get_value(self, date=None):
        self.ensure_one()
        if not date:
            date = fields.Date.today()
        value_records = self.value_ids.filtered(lambda v: v.date_from <= date)
        if not value_records:
            return
        value_record = value_records[0]
        if self.type == "text":
            return literal_eval('"{}"'.format(value_record.value_text))
        elif self.type == "reference":
            return value_record.value_reference

    _sql_constraints = [
        (
            "_unique",
            "unique (code, company_id)",
            "Two time parameters cannot have the same code.",
        ),
    ]
