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
    days_back = fields.Integer(string="Number of days", default=1)

    @api.model
    def generate_report(self, days_back=1):
        """Generate the profiler statistics report."""
        self.search([]).unlink()

        query = """
            SELECT name,
                   percentile_disc(0.95) WITHIN GROUP (ORDER BY duration) AS p95,
                   percentile_disc(0.99) WITHIN GROUP (ORDER BY duration) AS p99,
                   count(*) AS count
            FROM profiler_result
            WHERE create_date > now() - interval '%s day'
            GROUP BY name
            ORDER BY p99 DESC
            LIMIT 20
        """

        self.env.cr.execute(query, (days_back,))
        results = self.env.cr.fetchall()

        report_records = []
        for row in results:
            report_records.append(
                {
                    "name": row[0],
                    "p95": row[1],
                    "p99": row[2],
                    "count": row[3],
                    "days_back": days_back,
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
            "context": {"create": False, "edit": False, "delete": False},
        }

    def action_refresh(self):
        """Refresh the report with current data."""
        days_back = self[0].days_back if self else 1
        return self.generate_report(days_back=days_back)
