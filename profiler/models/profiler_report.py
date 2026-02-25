# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ProfilerReport(models.TransientModel):
    _name = "profiler.report"
    _description = "Profiler Statistics Report"

    name = fields.Char(string="Function Name")
    p95 = fields.Float(string="P95 Duration (s)", digits=(12, 6))
    p99 = fields.Float(string="P99 Duration (s)", digits=(12, 6))
    count = fields.Integer(string="Call Count")

    def _parse_time_delta(self, time_delta_str):
        """Parse time delta string in format HH:MM:SS and return total seconds."""
        try:
            parts = time_delta_str.split(":")
            if len(parts) != 3:
                raise ValueError("Invalid format")
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        except Exception:
            # Default to 24 hours if parsing fails
            return 86400

    @api.model
    def generate_report(self):
        """Generate the profiler statistics report."""
        self.search([]).unlink()

        # Get time_delta from context (format: "HH:MM:SS")
        time_delta_str = self.env.context.get("time_delta", "24:00:00")
        total_seconds = self._parse_time_delta(time_delta_str)

        query = """
            SELECT name,
                   percentile_disc(0.95) WITHIN GROUP (ORDER BY duration) AS p95,
                   percentile_disc(0.99) WITHIN GROUP (ORDER BY duration) AS p99,
                   count(*) AS count
            FROM profiler_result
            WHERE create_date > now() - interval '%s second'
            GROUP BY name
            ORDER BY p99 DESC
            LIMIT 20
        """

        self.env.cr.execute(query, (total_seconds,))
        results = self.env.cr.fetchall()

        report_records = []
        for row in results:
            report_records.append(
                {
                    "name": row[0],
                    "p95": row[1],
                    "p99": row[2],
                    "count": row[3],
                }
            )

        if report_records:
            self.create(report_records)

        return {
            "type": "ir.actions.act_window",
            "name": "Profiler Statistics Report",
            "res_model": "profiler.report",
            "view_mode": "list",
            "target": "current",
            "context": {
                "create": False,
                "edit": False,
                "delete": False,
                "time_delta": time_delta_str,
            },
        }

    def action_refresh(self):
        """Refresh the report with current data."""
        return self.generate_report()
