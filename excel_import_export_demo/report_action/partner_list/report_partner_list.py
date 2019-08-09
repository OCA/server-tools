# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class ReportPartnerList(models.TransientModel):
    _name = 'report.partner.list'
    _description = 'Wizard for report.partner.list'

    partner_ids = fields.Many2many(
        comodel_name='res.partner',
    )
    supplier = fields.Boolean(
        default=True,
    )
    customer = fields.Boolean(
        default=True,
    )
    results = fields.Many2many(
        'res.partner',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        """ On the wizard, result will be computed and added to results line
        before export to excel by report_excel action
        """
        self.ensure_one()
        domain = ['|', ('supplier', '=', self.supplier),
                  ('customer', '=', self.customer)]
        if self.partner_ids:
            domain.append(('id', 'in', self.partner_ids.ids))
        self.results = self.env['res.partner'].search(domain, order='id')
