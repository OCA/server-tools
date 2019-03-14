# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from openerp import models, fields, api


class ReportSaleOrder(models.TransientModel):
    _name = 'report.sale.order'
    _description = 'Wizard for report.sale.order'
    _inherit = 'xlsx.report'

    # Search Criteria
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    # Report Result, sale.order
    results = fields.Many2many(
        'sale.order',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing stored in database',
    )

    @api.multi
    def _compute_results(self):
        """ On the wizard, result will be computed and added to results line
        before export to excel, by using xlsx.export
        """
        self.ensure_one()
        Result = self.env['sale.order']
        domain = []
        if self.partner_id:
            domain += [('partner_id', '=', self.partner_id.id)]
        self.results = Result.search(domain)
