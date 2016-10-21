# -*- coding: utf-8 -*-
# Copyright <YEAR(S)> Daniel Reis <dreis.pt@hotmail.com>
# Copyright <YEAR(S)> Glen Dromgoole <gdromgoole@tier1engineering.com>
# Copyright <YEAR(S)> Loic Lacroix <loic.lacroix@savoirfairelinux.com>
# Copyright <YEAR(S)> Sandy Carter <sandy.carter@savoirfairelinux.com>
# Copyright <YEAR(S)>Gervais Naoussi <gervaisnaoussi@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class KPIHistory(models.Model):
    """History of the KPI."""

    _name = "kpi.history"
    _description = "History of the KPI"
    _order = "date desc"

    name = fields.Char('Name', size=150, required=True,
                       default=fields.Datetime.now(),)
    kpi_id = fields.Many2one('kpi', 'KPI', required=True)
    date = fields.Datetime(
        'Execution Date',
        required=True,
        readonly=True,
        default=fields.Datetime.now()
    )
    value = fields.Float('Value', required=True, readonly=True)
    color = fields.Text('Color', required=True,
                        readonly=True, default='#FFFFFF')
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.user.company_id.id)
