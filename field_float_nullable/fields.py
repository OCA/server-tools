# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import fields


class FloatNullable(fields.Float):
    """
    The FloatNullable field is a custom Odoo field type that extends the standard fields.Float
    to allow NULL values in the database column.
    By default, Odoo uses 0.0 as the default value for fields.Float, which can lead
    to ambiguity between "unset" and "zero" values.
    """

    type = "float_nullable"

    def convert_to_column(self, value, record, values=None, validate=True):
        if value is None or value == "" or value is False:
            return None
        return super().convert_to_column(
            value, record, values=values, validate=validate
        )

    def convert_to_cache(self, value, record, validate=True):
        if value is None or value == "" or value is False:
            return None
        return super().convert_to_cache(value, record, validate=validate)

    def convert_to_record(self, value, record):
        return value


fields.FloatNullable = FloatNullable
