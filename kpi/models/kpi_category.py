# -*- coding: utf-8 -*-
# Copyright <YEAR(S)> Daniel Reis <dreis.pt@hotmail.com>
# Copyright <YEAR(S)> Glen Dromgoole <gdromgoole@tier1engineering.com>
# Copyright <YEAR(S)> Loic Lacroix <loic.lacroix@savoirfairelinux.com>
# Copyright <YEAR(S)> Sandy Carter <sandy.carter@savoirfairelinux.com>
# Copyright <YEAR(S)>Gervais Naoussi <gervaisnaoussi@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class KPICategory(models.Model):
    """KPI Category."""

    _name = "kpi.category"
    _description = "KPI Category"
    name = fields.Char('Name', size=50, required=True)
    description = fields.Text('Description')
