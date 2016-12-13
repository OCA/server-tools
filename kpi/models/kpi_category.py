# -*- coding: utf-8 -*-
# Copyright 2012 - Now Savoir-faire Linux <https://www.savoirfairelinux.com/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class KPICategory(models.Model):
    """KPI Category."""

    _name = "kpi.category"
    _description = "KPI Category"
    name = fields.Char('Name', size=50, required=True)
    description = fields.Text('Description')
