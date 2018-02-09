# coding: utf-8
# © 2018 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class IrModel(models.Model):
    _inherit = "ir.model"

    onchange_rule_unavailable = fields.Boolean()
