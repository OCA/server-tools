# Copyright 2022 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
"""Models to test support for xlsx files."""
from odoo import fields, models

# pylint: disable=import-error
from odoo.addons.base_import.models.test_models import model


class PreviewModel(models.Model):
    """Test model for excel import."""

    _name = model("preview.excel")
    _description = "Tests : Base Import Model Preview for excel"

    name = fields.Char("Name")
    somevalue = fields.Integer(string="Some Value", required=True)
    othervalue = fields.Integer(string="Other Variable")
    counter = fields.Integer(string="Counter")
    date = fields.Date(string="Date")
    time = fields.Datetime(string="Time")
    amount = fields.Float(string="Amount")
