# Copyright 2025 Simone Rubino - PyTech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResGroups(models.Model):
    _inherit = "res.groups"

    trans_implied_ids = fields.Many2many(
        recursive=True,
    )
