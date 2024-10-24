# Copyright 2023 Omal Bastin (o4odoo@gmail.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ImageOwnerTest(models.Model):
    _inherit = "base_multi_image.owner"
    _name = "base_multi_image.owner.test"

    name = fields.Char(required=True)
