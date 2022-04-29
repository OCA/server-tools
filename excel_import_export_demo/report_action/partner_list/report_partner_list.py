# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ReportPartnerList(models.TransientModel):
    _name = "report.partner.list"
    _description = "Wizard for report.partner.list"

    partner_ids = fields.Many2many(comodel_name="res.partner")
    results = fields.Many2many(
        "res.partner",
        compute="_compute_results",
        help="Use compute fields, so there is nothing store in database",
    )

    def _compute_results(self):
        """On the wizard, result will be computed and added to results line
        before export to excel by report_excel action
        """
        self.ensure_one()
        domain = []
        if self.partner_ids:
            domain.append(("id", "in", self.partner_ids.ids))
        self.results = self.env["res.partner"].search(domain, order="id")
