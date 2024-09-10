# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from random import randint

from odoo import api, fields, models


class OcaUpdateTag(models.Model):

    _name = "oca.update.tag"
    _description = "Oca Update Tag"

    @api.model
    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(required=True)
    color = fields.Integer(default=lambda r: r._get_default_color())
