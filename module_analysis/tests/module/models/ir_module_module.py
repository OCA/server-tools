# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    test_field = fields.Char()
