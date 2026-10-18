# © 2023 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import uuid
from datetime import date, datetime, time, timedelta
from textwrap import dedent

from odoo import _, fields, models
from odoo.tools.safe_eval import safe_eval


class MonitoringScript(models.Model):
    _name = "monitoring.script"
    _description = _("Monitoring Check")
    _inherit = ["monitoring.output.mixin"]

    def _get_types(self):
        return [
            ("false", _("Expect False")),
            ("true", _("Expect True")),
            ("lower", _("Expect Lower")),
            ("higher", _("Expect Higher")),
        ]

    def _get_states(self):
        return [
            ("ok", _("OK")),
            ("warning", _("Warning")),
            ("critical", _("Critical")),
        ]

    monitoring_ids = fields.Many2many("monitoring")
    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    token = fields.Char(
        default=lambda self: str(uuid.uuid4()),
        readonly=True,
        copy=False,
        help="Token to use for the API",
    )
    state = fields.Selection("_get_states")
    check_type = fields.Selection(
        "_get_types",
        required=True,
        help="`Expect False` .. The result must be False to be not critical\n"
        "`Expect True` .. The result must be True to be not critical\n"
        "`Expect Lower` .. The result must be lower than the thresholds\n"
        "`Expect Higher` .. The result must be higher than the thresholds\n",
    )
    snippet = fields.Text(
        required=True,
        help="Monitoring script. Put the result into the variable `result`. "
        "With `env` you get an extra environment with OdooBot access levels.",
    )
    warning = fields.Float(help="Threshold for warning")
    critical = fields.Float(help="Threshold for critical")

    _sql_constraints = [
        ("token_uniq", "UNIQUE(token)", _("The token must be unique")),
    ]

    def _get_context(self):
        return {
            "date": date,
            "datetime": datetime,
            "time": time,
            "timedelta": timedelta,
        }

    def _evaluate(self):
        self.ensure_one()
        # Run it with an extra environment to prevent changes
        context = self._get_context()
        context.update({"result": None, "env": self.env})
        safe_eval(dedent(self.snippet).strip(), context, mode="exec", nocopy=True)
        return context.get("result")

    def _render(self, value=None):
        self.ensure_one()
        result = {"name": self.name, "check_type": self.check_type, "state": self.state}
        if value is not None:
            result["value"] = value
        if self.check_type in ("lower", "higher"):
            result.update({"warning": self.warning, "critical": self.critical})
        return result

    def _state_expect_bool(self, value, expect):
        if isinstance(value, bool) and value == expect:
            return "ok"
        return "critical"

    def _state_expect_threshold(self, value, warning, critical):
        if value >= critical:
            return "critical"
        if value >= warning:
            return "warning"
        return "ok"

    def validate(self, verbose=False):
        result = []
        for rec in self.with_context(active_test=False):
            value = rec._evaluate()

            if not isinstance(value, (int, float, bool)):
                rec.state = "critical"
            elif rec.check_type == "false":
                rec.state = rec._state_expect_bool(value, False)
            elif rec.check_type == "true":
                rec.state = rec._state_expect_bool(value, True)
            elif rec.check_type == "lower":
                rec.state = rec._state_expect_threshold(
                    value, rec.warning, rec.critical
                )
            elif rec.check_type == "higher":
                rec.state = rec._state_expect_threshold(
                    -value, -rec.warning, -rec.critical
                )
            else:
                raise NotImplementedError()

            if not rec.active:
                continue

            if verbose or rec.state in ("critical", "warning"):
                result.append(rec._render(value))

        return result

    def validate_and_format(self, verbose=False):
        self.ensure_one()

        result = self.validate(verbose=verbose)
        return self.format_output(result)
