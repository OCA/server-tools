# -*- coding: utf-8 -*-
# © 2020 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class BaseMergeModelLine(models.Model):

    _name = 'base.merge.model.line'

    merge_model_id = fields.Many2one(
        required=True)
    field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        required=True)
    # future extensions
    # operator = fields.Selected(
    # [('=', 'Strict equal'), ('=ilike', 'Case sensitive equal')])
    # domain = fields.Text()
