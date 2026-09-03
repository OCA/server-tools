# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrSequence(models.Model):
    _inherit = "ir.sequence"

    template_id = fields.Many2one("ir.sequence.template", ondelete="set null")
