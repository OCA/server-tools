# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ReportCRMLead(models.TransientModel):
    _name = "report.crm.lead"
    _description = "Wizard for report.crm.lead"
    _inherit = "xlsx.report"

    # Search Criteria
    team_id = fields.Many2one("crm.team", string="Sales Team")
    # Report Result, crm.lead
    results = fields.Many2many(
        "crm.lead",
        compute="_compute_results",
    )
    revenue_by_country = fields.Many2many(
        "crm.lead",
        compute="_compute_revenue_by_country",
    )
    revenue_by_team = fields.Many2many(
        "crm.lead",
        compute="_compute_revenue_by_team",
    )

    def _compute_results(self):
        self.ensure_one()
        domain = []
        if self.team_id:
            domain += [("team_id", "=", self.team_id.id)]
        self.results = self.env["crm.lead"].search(domain)

    def _compute_revenue_by_country(self):
        self.ensure_one()
        domain = []
        if self.team_id:
            domain += [("team_id", "=", self.team_id.id)]
        results = self.env["crm.lead"].read_group(
            domain,
            ["country_id", "expected_revenue"],
            ["country_id"],
            orderby="country_id",
        )
        for row in results:
            self.revenue_by_country += self.env["crm.lead"].new(
                {
                    "country_id": row["country_id"],
                    "expected_revenue": row["expected_revenue"],
                }
            )

    def _compute_revenue_by_team(self):
        self.ensure_one()
        domain = []
        if self.team_id:
            domain += [("team_id", "=", self.team_id.id)]
        results = self.env["crm.lead"].read_group(
            domain, ["team_id", "expected_revenue"], ["team_id"], orderby="team_id"
        )
        for row in results:
            self.revenue_by_team += self.env["crm.lead"].new(
                {"team_id": row["team_id"], "expected_revenue": row["expected_revenue"]}
            )
