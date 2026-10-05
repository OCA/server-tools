# Author Copyright (C) 2022 Nimarosa (Nicolas Rodriguez) (<nicolasrsande@gmail.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .base_time_parameter_version import _validate_boolean


class TimeParameter(models.Model):
    _name = "base.time.parameter"
    _description = "Time Parameter"

    name = fields.Char(string="Parameter Name")
    code = fields.Char()
    description = fields.Text()
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
    record_model = fields.Selection([])
    version_ids = fields.One2many(
        "base.time.parameter.version", "parameter_id", string=("Versions")
    )

    @api.model
    def _get_lookup_domain(self, model, code):
        """Return the domain of the parameters a lookup may use.

        The parameters of the current company and those with no company, the
        parameters of ``model`` (an ``ir.model`` record) and those with no
        model, by code -- or by name, for a parameter that has no code.

        This is a hook: a module that adds parameters which must not take
        part in the lookup extends the domain here.
        """
        return [
            ("company_id", "in", (self.env.company.id, False)),
            ("model_id", "in", (model.id, False)),
            "|",
            ("code", "=", code),
            "&",
            ("code", "=", False),
            ("name", "=", code),
        ]

    @api.model
    def _get_from_model_code_date(
        self, model_name, code, date=None, raise_if_not_found=True, get="value"
    ):
        # Filter on company, model, code/name
        # `_get` reads as superuser: asking for a parameter must not require
        # access rights on the models themselves.
        model = self.env["ir.model"]._get(model_name)
        parameters = self.search(self._get_lookup_domain(model, code))
        # The domain matches the parameters of the current company together
        # with the global ones (no company), and the parameters of the model
        # together with those that apply to any model. Sort the most specific
        # ones first so that a module may ship a global default that a company
        # overrides with its own parameter, instead of both matching at once.
        for parameter in parameters.sorted(
            key=lambda p: (bool(p.company_id), bool(p.model_id)), reverse=True
        ):
            # What decides is the version, not its value: the first parameter
            # with a version in force at that date is the answer, be it 0,
            # False or no value at all (None). Only a parameter with no
            # version at that date leaves the question to the next one.
            if parameter._get_version(date):
                return parameter._get(date, get=get)
        # No version in force
        if not raise_if_not_found:
            return
        # Raise error
        raise UserError(
            _(
                "No parameter for model '%(model_name)s', code '%(code)s', "
                "date %(date)s",
                model_name=model.name,
                code=code,
                date=date,
            )
        )

    def _get_version(self, date=None):
        """Return the version in force at ``date`` (today by default).

        That is the latest version starting on or before that date; an empty
        recordset when the parameter has none.
        """
        self.ensure_one()
        if not date:
            date = fields.Date.today()
        return self.version_ids.filtered(lambda v: v.date_from <= date).sorted(
            key=lambda v: v.date_from, reverse=True
        )[:1]

    def _get(self, date=None, get="value"):
        self.ensure_one()
        version = self._get_version(date)
        if not version:
            return False
        if get == "value":
            if self.type in ("record", "reference"):
                return version.value_reference or None
            elif self.type == "reference_id":
                return version.value_reference and version.value_reference.id or 0
            elif not version.value:
                # A version with no value: there is nothing to parse.
                return None
            elif self.type == "boolean":
                return _validate_boolean(version.value) == "True"
            elif self.type == "date":
                return datetime.strptime(version.value, "%Y-%m-%d").date()
            elif self.type == "float":
                return float(version.value)
            elif self.type == "integer":
                return int(version.value)
            elif self.type == "json":
                return json.loads(version.value)
            elif self.type == "string":
                return version.value
        elif get == "date":
            return version.date_from

    @api.constrains("type")
    def _check_version_values(self):
        """The versions are stored as text, parsed according to this type."""
        self.version_ids._check_value()

    _sql_constraints = [
        (
            "_unique",
            "unique (code, company_id)",
            "Two time parameters cannot have the same code.",
        ),
    ]
