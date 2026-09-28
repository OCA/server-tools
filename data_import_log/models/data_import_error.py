# Copyright 2020-2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class DataImportError(models.Model):
    _name = "data.import.error"
    _description = "Data Import Error"

    row_no = fields.Integer("Row Number")
    unit_key = fields.Char(
        help="The unit this error belongs to, which is what the file of "
        "rejected units is built from.",
    )
    reference = fields.Char()
    error_message = fields.Text("Message")
    log_id = fields.Many2one("data.import.log", string="Log")
