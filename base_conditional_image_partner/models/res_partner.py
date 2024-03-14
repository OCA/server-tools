# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "conditional.image.consumer.mixin"]

    def _compute_images(self):
        result = super()._compute_images()
        for rec in self:
            if not rec.image_1920:
                rec.update(
                    {
                        "image_1920": rec.avatar_1920,
                        "image_1024": rec.avatar_1024,
                        "image_512": rec.avatar_512,
                        "image_256": rec.avatar_256,
                        "image_128": rec.avatar_128,
                    }
                )
        return result
