# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models
from odoo.tools.safe_eval import safe_eval


class ConditionalImageConsumerMixin(models.AbstractModel):
    _name = "conditional.image.consumer.mixin"
    _description = "Mixin for conditional images consumers"
    _inherit = "image.mixin"

    image_1920 = fields.Image(compute="_compute_images", store=False, readonly=True)
    image_1024 = fields.Image(compute="_compute_images", store=False, readonly=True)
    image_512 = fields.Image(compute="_compute_images", store=False, readonly=True)
    image_256 = fields.Image(compute="_compute_images", store=False, readonly=True)
    image_128 = fields.Image(compute="_compute_images", store=False, readonly=True)

    def _conditional_image_evaluate_selector(self, conditional_image):
        self.ensure_one()
        if conditional_image.selector:
            if (
                conditional_image.company_id == self.company_id
                or self.company_id
                and not conditional_image.company_id
            ):
                return bool(
                    safe_eval(conditional_image.selector or "True", {"object": self})
                )
        return False

    def _compute_images(self):
        if "company_id" in self._fields:
            search_clause = [("model_name", "=", self._name)]
        else:
            # If inherited object doesn't have a `company_id` field,
            # remove the items with a company defined and the related checks
            search_clause = [
                ("model_name", "=", self._name),
                ("company_id", "=", False),
            ]

        conditional_images = self.env["conditional.image"].search(
            search_clause, order="company_id, selector"
        )

        for record in self:
            images_found = conditional_images.filtered(
                lambda img: record._conditional_image_evaluate_selector(img)
            )
            values = {
                "image_1920": False,
                "image_1024": False,
                "image_512": False,
                "image_256": False,
                "image_128": False,
            }
            if images_found:
                image = images_found[0]
                values = {
                    "image_1920": image.image_1920,
                    "image_1024": image.image_1024,
                    "image_512": image.image_512,
                    "image_256": image.image_256,
                    "image_128": image.image_128,
                }
            record.update(values)
