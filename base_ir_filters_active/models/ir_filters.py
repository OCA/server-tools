# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class IrFilters(models.Model):
    _inherit = 'ir.filters'

    active = fields.Boolean(default=True)
