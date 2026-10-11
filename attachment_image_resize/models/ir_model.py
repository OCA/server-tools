# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class IrModel(models.Model):
    _inherit = "ir.model"

    attachment_image_max_resolution = fields.Char(
        help="This resolution will be applied to the resizing of images"
        " for this model."
    )
