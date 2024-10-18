# © 2024 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MonitoringOutputMixin(models.AbstractModel):
    _name = "monitoring.output.mixin"
    _description = _("Mixin for the Monitoring Output")

    def _get_output_format(self):
        return [("json", "JSON"), ("prometheus", "Prometheus")]

    output_format = fields.Selection(
        "_get_output_format", default="json", required=True
    )
    prometheus_metric = fields.Char(default="odoo_metric")
    prometheus_label = fields.Char(default="check")

    @api.constrains("output_format", "prometheus_metric", "prometheus_label")
    def _check_prometheus_metric(self):
        regex = re.compile(r"^[a-zA-Z0-9:_]+$")
        for rec in self:
            if rec.output_format != "prometheus":
                continue

            if not regex.match(rec.prometheus_metric):
                raise ValidationError(_("Invalid metric naming"))

            if not regex.match(rec.prometheus_label):
                raise ValidationError(_("Invalid label naming"))

    def format_output(self, result):
        formatter = getattr(self, f"format_{self.output_format}", None)
        if callable(formatter):
            return formatter(self.state, result)

        raise NotImplementedError()

    def response_headers(self):
        self.ensure_one()
        if self.output_format == "json":
            return {"Content-Type": "application/json"}
        if self.output_format == "prometheus":
            return {"Content-Type": "text/plain"}
        raise NotImplementedError()

    def format_json(self, state, result):
        return json.dumps({"status": state, "checks": result})

    def format_prometheus_line(self, name, value, labels=None):
        def escape(v):
            return v.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')

        if labels:
            # flake8: noqa: B907
            labels = (
                "{" + ",".join(f'{k}="{escape(v)}"' for k, v in labels.items()) + "}"
            )
        else:
            labels = ""

        return f"{name}{labels} {value}"

    def format_prometheus(self, state, result):
        metric = self.prometheus_metric
        keys = ("name", "value", "state")

        lines = [
            tuple(map(check.get, keys))
            for check in result
            if all(k in check for k in keys)
        ]

        output = [
            f"# HELP {metric}_value Monitored value of the metric",
            f"# TYPE {metric}_value gauge",
            *[
                self.format_prometheus_line(
                    f"{metric}_value",
                    int(value) if isinstance(value, bool) else value,
                    {self.prometheus_label: name},
                )
                for name, value, state in lines
            ],
            f"# HELP {metric}_warning Metric is in a warning state",
            f"# TYPE {metric}_warning gauge",
            *[
                self.format_prometheus_line(
                    f"{metric}_warning",
                    int(state == "warning"),
                    {self.prometheus_label: name},
                )
                for name, value, state in lines
            ],
            f"# HELP {metric}_critical Metric is in a critical state",
            f"# TYPE {metric}_critical gauge",
            *[
                self.format_prometheus_line(
                    f"{metric}_critical",
                    int(state == "critical"),
                    {self.prometheus_label: name},
                )
                for name, value, state in lines
            ],
        ]
        return "\n".join(output) + "\n"
