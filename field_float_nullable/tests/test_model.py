# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class TestFloatNullableModel(models.Model):
    _name = "test.float.nullable"
    _description = "Test Model for Float Nullable"

    name = fields.Char(required=True)
    value_float = fields.Float(string="Standard Float")
    value_float_nullable = fields.FloatNullable(string="Nullable Float")
