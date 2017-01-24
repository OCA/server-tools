# -*- coding: utf-8 -*-
# Copyright 2016 - Ursa Information Systems <http://ursainfosystems.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models, fields


class IrModelAccess(models.Model):
    _inherit = 'ir.model.access'

    perm_export = fields.Boolean('Export Access', default=True)
